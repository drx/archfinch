from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.utils.http import base36_to_int
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django import forms
from archfinch.main.models import Opinion, Similarity, Category, Item, Review, Action
from archfinch.users.models import User


def get_max_similarity(user):
    this_user = User.objects.filter(pk=user).annotate(Max('similarity__value')).values_list('similarity__value__max', flat=True)[0]
    if not this_user:
        this_user = 0
    try:
        all_users = Similarity.objects.order_by('-value')[0].value
    except IndexError:
        all_users = 0
    potential = user.opinion_set.count()

    return locals()


def reviews(request, username, start=None, n=None):
    if start is None:
        start = 0
    else:
        start = int(start)
    
    if n is None or not 0 < int(n) < 10:
        n = 10
    else:
        n = int(n)
    review_user = get_object_or_404(User, username=username)

    reviews = Review.objects.filter(user=review_user).extra(
        select={
            'rating': 'SELECT rating FROM main_opinion WHERE main_opinion.item_id=main_review.item_id AND main_opinion.user_id=main_review.user_id',
            'time': 'SELECT time FROM main_action WHERE main_review.id=main_action.review_id AND type=2',
        },
    ).select_related('item').order_by('-time')

    count = reviews.count()
    left = count-(start+n)
    reviews = reviews[start:start+n]

    for review in reviews:
        review.rating_verbose = Opinion(rating=review.rating).get_third_person()

    single = False

    return render_to_response('user/reviews.html', locals(), context_instance=RequestContext(request))


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


def overview(request, username, category_slug=None, start=None, n=None, json=None):
    viewed_user = get_object_or_404(User, username=username)

    print json

    if start is None:
        start = 0
    else:
        start = int(start)
    
    if n is None or not 0 < int(n) < 100:
        n = 100
    else:
        n = int(n)

    if category_slug is not None and category_slug:
        category = Category.objects.get(slug=category_slug)
    else:
        category = None

    categories = viewed_user.categories()
    your_profile = False
    if request.user==viewed_user or not request.user.is_authenticated():
        if request.user==viewed_user:
            your_profile = True

        opinions = Opinion.objects.filter(user__exact=viewed_user).select_related('item__category').order_by('-rating','item__name').extra(
            select={'review': 'SELECT EXISTS (SELECT 1 FROM main_review WHERE main_review.user_id = %s AND main_review.item_id = main_item.id)'},
            select_params=[viewed_user.id],
        )
        if category is not None:
            opinions = opinions.filter(item__category=category)
        else:
            opinions = opinions.filter(item__category__hide=False)

        similarity = 0
        similarity_max = 10

    else:
        opinions = Opinion.objects.opinions_of(viewed_user, request.user, category=category)

        similarity_max = get_max_similarity(request.user)

        try:
            similarity = viewed_user.similarity_set.get(
                user2=request.user.id).value
        except ObjectDoesNotExist:
            similarity = 0

    lists = viewed_user.list_set.all()

    count = len(list(opinions))
    left = count-(start+n)
    opinions = opinions[start:start+n]

    return render_to_response('user/overview.html',
        locals(), context_instance=RequestContext(request))


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

def similar(request, start=None, n=None):
    '''
    Show users most similar to the logged in user.
    '''

    if request.user.is_authenticated():
        if start is None:
            start = 0
        else:
            start = int(start)
        
        if n is None or not 0 < int(n) < 10:
            n = 10
        else:
            n = int(n)

        similarity_max = get_max_similarity(request.user)
        similar_users = request.user.similar()
        count = similar_users.count()
        similar_users = similar_users[start:start+n]
        likes = likes_gen(similar_users, request.user)

        left = count-(start+n)

        return render_to_response('user/similar.html', locals(), context_instance=RequestContext(request))
    else:
        return render_to_response('user/similar_anonymous.html', context_instance=RequestContext(request))
