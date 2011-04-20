from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from archfinch.utils import render_to_response
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.utils.http import base36_to_int
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, Count, StdDev
from django import forms
from archfinch.main.models import Opinion, Similarity, Category, Item, Review, Action
from archfinch.users.models import User
from django.utils.datastructures import SortedDict
from lazysignup.decorators import allow_lazy_user
from django.core.cache import cache
from archfinch.utils import paginate

def get_max_similarity(user):
    try:
        this_user = User.objects.filter(pk=user).annotate(Max('similarity__value')).values_list('similarity__value__max', flat=True)[0]
        if not this_user:
            this_user = 0
    except IndexError:
        this_user = 0        
    try:
        all_users = Similarity.objects.order_by('-value')[0].value
    except IndexError:
        all_users = 0
    potential = user.opinion_set.count()

    return locals()


@allow_lazy_user
def top_users(request):
    top_users = User.objects.order_by('-karma')[:10]

    return render_to_response('user/top_users.html', locals(), context_instance=RequestContext(request))


@allow_lazy_user
def reviews(request, username, page=None):
    if page is None:
        page = 1
    else:
        page = int(page)
    
    n = 10

    review_user = get_object_or_404(User, username=username)

    reviews = Review.objects.filter(user=review_user).extra(
        select={
            'rating': 'SELECT rating FROM main_opinion WHERE main_opinion.item_id=main_review.item_id AND main_opinion.user_id=main_review.user_id',
            'time': 'SELECT time FROM main_action WHERE main_review.id=main_action.review_id AND type=2',
        },
    ).select_related('item').order_by('-time')

    # pagination
    reviews, paginator, current_page, page_range = paginate(reviews, page, n)

    for review in reviews:
        review.rating_verbose = Opinion(rating=review.rating).get_third_person()

    single = False

    return render_to_response('user/reviews.html', locals(), context_instance=RequestContext(request))


@allow_lazy_user
def review_show(request, username, item_id):
    item_id = base36_to_int(item_id)
    review_user = get_object_or_404(User, username=username)
    item = get_object_or_404(Item, pk=item_id)
    review = get_object_or_404(Review, user=review_user, item=item)
    try:
        opinion = review_user.opinion_set.get(item=item)
    except Opinion.DoesNotExist:
        opinion = None

    time = Action.objects.get(review=review, type=Action.types['review']).time

    reviews = [{'item': item, 'text': review.text, 'rating': opinion.rating, 'rating_verbose': opinion.get_third_person(), 'time': time}]
    single = True

    return render_to_response('user/reviews.html', locals(), context_instance=RequestContext(request))


class ReviewForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 100, 'rows': 20, 'class': 'resizable'})
    )


@allow_lazy_user
def review_edit(request, item_id):
    item = get_object_or_404(Item, pk=base36_to_int(item_id))

    try:
        review = request.user.review_set.get(item=item)
    except Review.DoesNotExist:
        review = None

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            if review is None:
                review = Review(item=item, user=request.user, text=text)
                review.save()
            else:
                review.text = text
                review.save()

            action, created = Action.objects.get_or_create(type=Action.types['review'], review=review, user=request.user)
            action.save()

            return HttpResponseRedirect(reverse('review', args=[request.user.username, item_id, slugify(item.name)]))
    else:
        if review is not None:
            text = review.text
        else:
            text = ''
        form = ReviewForm(initial={'text': text})

    return render_to_response('user/review_edit.html', locals(), context_instance=RequestContext(request))


@allow_lazy_user
def overview(request, username, category_slug=None, page=None, json=None):
    viewed_user = get_object_or_404(User, username=username)

    if page is None:
        page = 1
    else:
        page = int(page)
    
    n = 100

    if category_slug is not None and category_slug:
        category = Category.objects.get(slug=category_slug)
    else:
        category = None

    hide = False
    if viewed_user.id == 1:
        # don't show drx's links
        hide = True
    categories = viewed_user.categories(hide=hide)
    your_profile = False
    if request.user==viewed_user:
        your_profile = True

    select=[
        ('review', 'SELECT EXISTS (SELECT 1 FROM main_review WHERE main_review.user_id = %s AND main_review.item_id = main_item.id)'),
        ('action_time', 'SELECT time FROM main_action WHERE main_action.opinion_id = main_opinion.id')
    ]
    select_params=[viewed_user.id]

    if request.user.is_authenticated():
        select += [('your_rating', 'SELECT rating FROM main_opinion mo2 WHERE mo2.user_id = %s AND mo2.item_id = main_item.id')]
        select_params += [request.user.id]

    show_controversial = False

    select = SortedDict(select)

    opinions = Opinion.objects.filter(user__exact=viewed_user).select_related('item__category').order_by('-action__time', '-rating','item__name').extra(
        select=select, select_params=select_params
    )
    if category is not None:
        opinions = opinions.filter(item__category=category)
    else:
        opinions = opinions.exclude(item__category__name='Lists')
    if hide:
        opinions = opinions.filter(item__category__hide=False)

    category_counts = viewed_user.categories(hide=hide)

    if request.user==viewed_user or not request.user.is_authenticated():
        similarity = 0
        similarity_max = 10

    else:
        similarity_max = get_max_similarity(request.user)

        try:
            similarity = viewed_user.similarity_set.get(
                user2=request.user.id).value
        except ObjectDoesNotExist:
            similarity = 0

    lists = viewed_user.list_set.all()

    # pagination
    opinions, paginator, current_page, page_range = paginate(opinions, page, n)

    if json:
        return render_to_response('user/overview.json', locals(), context_instance=RequestContext(request), mimetype='application/json')
    else:
        return render_to_response('user/overview.html', locals(), context_instance=RequestContext(request))


@allow_lazy_user
def referral(request, username):
    referrer = get_object_or_404(User, username=username)

    from lazysignup.utils import is_lazy_user
    if is_lazy_user(request.user) and not request.user.referred_by:
        request.user.referred_by = referrer
        request.user.save()

    return HttpResponseRedirect('/') 


def likes_gen(users, request_user):
    for user in users:
        likes = user.user2.opinion_set.filter(rating__gte=4).extra(
            where=['EXISTS (SELECT 1 FROM main_opinion mo WHERE mo.user_id=%s AND mo.item_id=main_opinion.item_id AND mo.rating >= 4)'],
            params=[request_user.id]
        ).order_by('-rating')[:5]
        items = likes.values_list('item__name', flat=True)
        if items:
            out = ', '.join(items[:4])
            out += '.' if len(items) < 5 else '...'
            yield out
        else:
            yield None


@allow_lazy_user
def similar(request, page=None):
    '''
    Show users most similar to the logged in user.
    '''

    if request.user.is_authenticated():
        if page is None:
            page = 1
        else:
            page = int(page)

        n = 10
        
        similarity_max = get_max_similarity(request.user)
        similar_users = request.user.similar()
        count = similar_users.count()

        # pagination
        similar_users, paginator, current_page, page_range = paginate(similar_users, page, n)

        likes = likes_gen(similar_users, request.user)

        return render_to_response('user/similar.html', locals(), context_instance=RequestContext(request))
    else:
        return render_to_response('user/similar_anonymous.html', context_instance=RequestContext(request))
