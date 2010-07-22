from django.http import HttpResponse
#from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from main.models import Opinion, Similarity
from users.models import User
from django.db.models import Max


def get_max_similarity(user):
    this_user = User.objects.filter(pk=user).annotate(Max('similarity__value')).values_list('similarity__value__max', flat=True)[0]
    all_users = Similarity.objects.order_by('-value')[0].value
    potential = user.opinion_set.count()

    return locals()

def overview(request, username):
    viewed_user = get_object_or_404(User, username=username)

    if request.user.is_authenticated():
        if request.user==viewed_user:
            your_profile = True

            opinions = Opinion.objects.filter(user__exact=request.user
                ).select_related('item__category').order_by('-rating','item__name')
            categories = request.user.categories()
            similarity = None
            similarity_max = 10
        else:
            your_profile = False
            opinions = Opinion.objects.opinions_of(viewed_user, request.user)
            categories = []

            # this is only for testing and should be removed
            Similarity.objects.update_user_pair(viewed_user, request.user)
            #Similarity.objects.update_user(viewed_user)

            similarity_max = get_max_similarity(request.user)

            try:
                similarity = viewed_user.similarity_set.get(
                    user2=request.user.id).value
            except ObjectDoesNotExist:
                similarity = None
        return render_to_response('user/overview.html',
            locals(), context_instance=RequestContext(request))
    else:
        opinions = []  # TODO: fix this
        return render_to_response('user/overview_anonymous.html',
            {'viewed_user': viewed_user, 'opinions': opinions},
            context_instance=RequestContext(request))


def likes_gen(users):
    for user in users:
        likes = user.user2.opinion_set.filter(rating__gte=4).order_by('-rating')[:5]
        items = likes.values_list('item__name', flat=True)
        out = ', '.join(items[:4])
        out += '.' if len(items) < 5 else '...'

        yield out

def similar(request):
    '''
    Show users most similar to the logged in user.
    '''

    if request.user.is_authenticated():
        start = 0
        length = 10
        similarity_max = get_max_similarity(request.user)
        similar_users = request.user.similar()[start:length]
        likes = likes_gen(similar_users)
        return render_to_response('user/similar.html',
            {'similar_users': similar_users,
            'similarity_max': similarity_max,
            'likes': likes},
            context_instance=RequestContext(request))
    else:
        return render_to_response('user/similar_anonymous.html',
            context_instance=RequestContext(request))
