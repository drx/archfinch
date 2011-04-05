from django.shortcuts import get_object_or_404, HttpResponse, redirect
from django.template import RequestContext
from django.utils import simplejson
from django.utils.http import base36_to_int, int_to_base36
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.db.models import Count
from archfinch.main.models import Item, Opinion, Action, Similarity, Category
from archfinch.main.forms import AddItemForm1, AddItemForm2, AddItemWizard
from archfinch.users.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.markup.templatetags.markup import markdown
from django.views.decorators.csrf import csrf_exempt
from archfinch.utils import render_to_response
from archfinch.main import tasks
import celery.result
from django.core.cache import cache
from lazysignup.decorators import allow_lazy_user
from django.conf import settings
from archfinch.utils import paginate

@allow_lazy_user
def welcome(request):
    if request.user.is_authenticated():
        return redirect(reverse('fresh'))
    else:
        return render_to_response("main/welcome_anonymous.html", context_instance=RequestContext(request))


@allow_lazy_user
def missing(request):
    wiz = AddItemWizard([AddItemForm1, AddItemForm2])
    return wiz(request, model=Item)


@allow_lazy_user
def item(request, item_id):
    '''
    Item page.
    '''

    item_id = base36_to_int(item_id)
    item = get_object_or_404(Item.objects.select_related('category', 'profile'), pk=item_id)

    if item.category_id == 8:
        return redirect(reverse('list-view', args=[int_to_base36(item_id), slugify(item.name)]))

    if request.user.is_authenticated():
        also_liked = item.also_liked(user=request.user)
        try:
            opinion = request.user.opinion_set.get(item=item)
        except Opinion.DoesNotExist:
            opinion = None
            recommendation = item.recommendation(request.user)
    else:
        opinion = None
        also_liked = item.also_liked()

    return render_to_response("main/item.html", locals(), context_instance=RequestContext(request))


def item_also_liked(request, item_id, like, also_like):
    '''
    "People who (dis)like x also (dis)like ys".
    '''

    item_id = base36_to_int(item_id)
    item = get_object_or_404(Item, pk=item_id)
    like = like == 'true'
    also_like = also_like == 'true'

    result_html = render_to_string('includes/also_liked.html', {'items': item.also_liked(like=like, also_like=also_like)}, context_instance=RequestContext(request))

    json = simplejson.dumps({'success': True, 'items': result_html})
    return HttpResponse(json, mimetype='application/json')


@allow_lazy_user
def recommend(request, category_slug=None, page=None, usernames=None, fresh=None):
    '''
    Shows a list of recommendations.
    '''
    if request.user.is_authenticated() or usernames is not None:
        if page is None:
            page = 1
        else:
            page = int(page)
        
        if category_slug is not None and category_slug:
            category = Category.objects.get(slug=category_slug)
        else:
            category = None

        n = 100
        if category and category.name in ('Videos', 'Pics') or fresh:
                n = 10

        if usernames is not None:
            usernames = usernames.split(',')
            users = list(map(lambda un: get_object_or_404(User, username=un), usernames))
            usernames_specified = True

        else:
            usernames = [request.user.username]
            users = [request.user]
            usernames_specified = False

        user_ids = map(lambda u: u.id, users)
        usernames_k = '+'.join(sorted(set(map(str, user_ids))))
        usernames_joined = ','.join(usernames)

        opinion_count = users[0].__class__.objects.filter(pk__in=user_ids).aggregate(Count('opinion'))['opinion__count']
        if opinion_count < 10:
            generic = True
            usernames_k = '#generic'
        else:
            generic = False
    
        cache_key = 'recommend,%s,%s,%s' % (usernames_k, category_slug, fresh)
        if settings.DEBUG:
            cache_timeout = 30
        else:
            cache_timeout = 15*60

        cached_value = cache.get(cache_key)

        computed = False
        if cached_value is not None:
            if type(cached_value) == tuple and cached_value[0] == 'task':
                recommendations = celery.result.AsyncResult(cached_value[1])
            else:
                recommendations = cached_value
                computed = True

        else:
            if generic:
                recommendations = tasks.recommend_generic.delay(category, fresh)
            else:
                recommendations = tasks.recommend.delay(category, fresh, users)
            task_id = recommendations.task_id
            cache.set(cache_key, ('task', task_id), cache_timeout)

        if not computed and recommendations.ready():
            recommendations = recommendations.result
            cache.set(cache_key, recommendations, cache_timeout)
            computed = True

        if not computed:
            wait_page = 'recommend'
            return render_to_response("main/wait.html", locals(), context_instance=RequestContext(request))
        else:

            # pagination
            recommendations, paginator, current_page, page_range = paginate(recommendations, page, n)

            if category is not None and category.id in (9,10,11) or fresh:
                # links
                for r in recommendations:
                    try:
                        r.rating = request.user.opinion_set.get(item__id=r.id).rating
                    except Opinion.DoesNotExist:
                        pass
                return render_to_response("links/recommend.html", locals(), context_instance=RequestContext(request))
            else:
                user_categories = request.user.categories()
                categories = Category.objects.filter(hide=False).order_by('name').values_list('id', 'element_plural', 'slug')
                return render_to_response("main/recommend.html", locals(), context_instance=RequestContext(request))


            
    else:
        return render_to_response("main/recommend_anonymous.html", context_instance=RequestContext(request))


def opinion_set(request, item_id, rating):
    '''
    Set rating for a (user, item) pair.

    Note: this is temporary and should be ajaxified later.
    '''

    item_id = base36_to_int(item_id)
    rating = int(rating)
    item = get_object_or_404(Item, pk=item_id)

    if not request.user.is_authenticated():
        json = simplejson.dumps({'success': False,
            'error_msg': 'You need to be logged in to set a rating.'})
        return HttpResponse(json, mimetype='application/json')

    tasks.opinion_set.delay(request.user, item, rating)

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

    tasks.opinion_remove.delay(request.user, item)

    json = simplejson.dumps({'success': True})
    return HttpResponse(json, mimetype='application/json')


def task_wait_error(request):
    """Raise a task_wait error to log request data etc."""
    raise Exception("task_wait_error");


def task_wait(request, task_id):
    data = {'success': False}
    if request.method == 'GET':
        task = celery.result.AsyncResult(task_id)
        task.get()
        
        data['success'] = True

    else:
        data['error_msg'] = 'Wrong request method'

    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')


@csrf_exempt
def process_markdown(request):
    data = {'success': False}
    if request.method == 'POST':
        text = request.POST['text']
        
        data['success'] = True
        data['html'] = markdown(text)

    else:
        data['error_msg'] = 'Wrong request method'

    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')
