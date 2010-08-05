from django.http import HttpResponse
#from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from main.models import Opinion, Similarity, Category
from users.models import User
from django.db.models import Max


def get_max_similarity(user):
    this_user = User.objects.filter(pk=user).annotate(Max('similarity__value')).values_list('similarity__value__max', flat=True)[0]
    all_users = Similarity.objects.order_by('-value')[0].value
    potential = user.opinion_set.count()

    return locals()


def overview(request, username, category_slug=None, start=None, n=None):
    viewed_user = get_object_or_404(User, username=username)

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

        opinions = Opinion.objects.filter(user__exact=viewed_user
            ).select_related('item__category').order_by('-rating','item__name')
        if category is not None:
            opinions = opinions.filter(item__category=category)

        similarity = None
        similarity_max = 10

    else:
        opinions = Opinion.objects.opinions_of(viewed_user, request.user, category=category)

        # this is only for testing and should be removed
        Similarity.objects.update_user_pair(viewed_user, request.user)
        #Similarity.objects.update_user(viewed_user)

        similarity_max = get_max_similarity(request.user)

        try:
            similarity = viewed_user.similarity_set.get(
                user2=request.user.id).value
        except ObjectDoesNotExist:
            similarity = None

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
