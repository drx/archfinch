from django.shortcuts import (render_to_response, get_object_or_404,
    HttpResponse)
from django.template import RequestContext
from django.utils import simplejson
from django.utils.http import base36_to_int
from main.models import Item, Opinion, Action, Similarity, Category


def welcome(request):
    if request.user.is_authenticated():
        return render_to_response("main/welcome.html",
            context_instance=RequestContext(request))
    else:
        return render_to_response("main/welcome_anonymous.html",
            context_instance=RequestContext(request))


def missing(request):
    return render_to_response("main/missing.html",
        context_instance=RequestContext(request))


def item(request, item_id):
    '''
    Item page.
    '''

    item_id = base36_to_int(item_id)
    item = get_object_or_404(Item, pk=item_id)

    if request.user.is_authenticated():
        try:
            opinion = request.user.opinion_set.get(item=item)
        except Opinion.DoesNotExist:
            opinion = None
    else:
        opinion = None

    return render_to_response("main/item.html",
        {'item': item, 'opinion': opinion},
        context_instance=RequestContext(request))


def recommend(request, category_slug=None, start=None, n=None):
    '''
    Shows a list of recommendations.
    '''

    if request.user.is_authenticated():
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

        user_categories = request.user.categories()
        categories = Category.objects.order_by('name').values_list('id', 'element_plural', 'slug')

        recommendations = list(request.user.recommend(category=category))

        count = len(recommendations)
        left = count-(start+n)
        recommendations = recommendations[start:start+n]

        return render_to_response("main/recommend.html",
            locals(), context_instance=RequestContext(request))
    else:
        return render_to_response("main/recommend_anonymous.html",
            context_instance=RequestContext(request))


def opinion_set(request, item_id, rating):
    '''
    Set rating for a (user, item) pair.

    Note: this is temporary and should be ajaxified later.
    '''

    item_id = base36_to_int(item_id)
    rating = int(rating)
    item = get_object_or_404(Item, pk=item_id)

    if not request.user.is_authenticated():
        # perhaps this is an opportunity to capture a yet unregistered user
        #  and shouldn't be an error
        json = simplejson.dumps({'success': False,
            'error_msg': 'You need to be logged in to set a rating.'})
        return HttpResponse(json, mimetype='application/json')

    # this should be forwarded to a server which does this kind of work
    #  and not done during the client request
    # also, this should update similarities
    action = Action()
    action.save()
    opinion, created = Opinion.objects.get_or_create(user=request.user,
        item=item, defaults={'action': action})
    old_rating = opinion.rating
    opinion.rating = rating
    opinion.action = action
    opinion.save()

    if created or rating != old_rating:
        delta = {item_id: ('set', old_rating, rating)}
        Similarity.objects.update_user_delta(request.user, delta)

    json = simplejson.dumps({'success': True})
    return HttpResponse(json, mimetype='application/json')


def opinion_remove(request, item_id):
    '''
    Remove rating for a (user, item) pair.

    Note: this is temporary and should be ajaxified later.
    '''

    item_id = base36_to_int(item_id)
    item = get_object_or_404(Item, pk=item_id)

    if not request.user.is_authenticated():
        json = simplejson.dumps({'success': False,
            'error_msg': 'You need to be logged in to remove a rating.'})
        return HttpResponse(json, mimetype='application/json')

    # see a similar comment for opinion_set
    opinion = Opinion.objects.get(user=request.user, item=item)
    old_rating = opinion.rating
    opinion.delete()

    delta = {item_id: ('remove', old_rating)}
    Similarity.objects.update_user_delta(request.user, delta)

    json = simplejson.dumps({'success': True})
    return HttpResponse(json, mimetype='application/json')
