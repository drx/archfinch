from django.shortcuts import get_object_or_404, HttpResponse, HttpResponseRedirect, redirect
from django.template import RequestContext
from django.utils import simplejson
from django.utils.http import base36_to_int, int_to_base36
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.db.models import Count
from archfinch.main.models import Item, Opinion, Action, Similarity, Category, Tag, TagBlock
from archfinch.main.forms import AddItemForm1, AddItemForm2, AddItemWizard
from archfinch.users.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.markup.templatetags.markup import markdown
from django.views.decorators.csrf import csrf_exempt
from archfinch.utils import render_to_response
from archfinch.utils.cache import publish_static
from archfinch.main import tasks
import celery.result
from django.core.cache import cache
from lazysignup.decorators import allow_lazy_user
from django.conf import settings
from archfinch.utils import paginate


@allow_lazy_user
def missing(request):
    wiz = AddItemWizard([AddItemForm1, AddItemForm2])
    return wiz(request, model=Item)


@publish_static
def item(request, item_id, publish=False):
    '''
    Item page.
    '''

    item_id = base36_to_int(item_id)
    item = get_object_or_404(Item.objects.select_related('category', 'profile'), pk=item_id)

    if item.is_comment():
        # item is a comment, so let's show its root and highlight it instead
        root = item.root()
        selected_path = root.path
        item, selected_comment_id = root, item.id

    else:
        selected_path = None

    comment_tree = item.comment_tree(selected_path=selected_path, user=request.user)
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

    response = render_to_response("main/item.html", locals(), context_instance=RequestContext(request))
    response.publish_static = True
    return response


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


@publish_static
def recommend(request, category_slug=None, page=None, usernames=None, tag_names=None, publish=False):
    '''
    Shows a list of recommendations.
    '''
    if page is None:
        page = 1
    else:
        page = int(page)
     
    fresh = False
    tags = None
    if tag_names:
        fresh = True
        category = None
        tag_names = tag_names.split('/')
        tags = Tag.objects.filter(name__in=tag_names)

    elif category_slug is not None and category_slug:
        if category_slug == 'fresh':
            fresh = True
            category = None
        else:
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

    try:
        opinion_count = users[0].__class__.objects.filter(pk__in=user_ids).aggregate(Count('opinion'))['opinion__count']
        if opinion_count < 10:
            generic = True
        else:
            generic = False
    except AttributeError:
        generic = True

    if generic:
        usernames_k = '#generic'

    if tag_names:
        tag_names_k = ','.join(tag_names)
    else:
        tag_names_k = ''

    cache_key = 'recommend;%s;%s;%s' % (usernames_k, category_slug, tag_names_k)
    if settings.DEBUG:
        cache_timeout = 30
    else:
        cache_timeout = 15*60

    cached_value = cache.get(cache_key)

    computed = False
    if cached_value is not None:
        if type(cached_value) == tuple and cached_value[0] == 'task':
            task_id = cached_value[1]
            recommendations = celery.result.AsyncResult(task_id)
        else:
            recommendations = cached_value
            computed = True

    else:
        if generic:
            recommendations = tasks.recommend_generic.delay(category, fresh, tags)
        else:
            recommendations = tasks.recommend.delay(category, fresh, tags, users)
        task_id = recommendations.task_id
        cache.set(cache_key, ('task', task_id), cache_timeout)

    if not computed and recommendations.ready():
        recommendations = recommendations.result
        cache.set(cache_key, recommendations, cache_timeout)
        computed = True

    if not computed and publish:
        recommendations = recommendations.get()
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
            response = render_to_response("links/recommend.html", locals(), context_instance=RequestContext(request))
        else:
            user_categories = request.user.categories()
            categories = Category.objects.filter(hide=False).order_by('name').values_list('id', 'element_plural', 'slug')
            response = render_to_response("main/recommend.html", locals(), context_instance=RequestContext(request))

        response.publish_static = True
        return response


@allow_lazy_user
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


@allow_lazy_user
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


@allow_lazy_user
def add_tag(request, item_id):
    '''
    Add a tag.
    '''

    item_id = base36_to_int(item_id)
    item = get_object_or_404(Item, pk=item_id)
    tag = request.GET['tag']

    if not request.user.is_authenticated():
        json = simplejson.dumps({'success': False,
            'error_msg': 'You need to be logged in to set a rating.'})
        return HttpResponse(json, mimetype='application/json')


    item.add_tag(tag, request.user)

    json = simplejson.dumps({'success': True})
    return HttpResponse(json, mimetype='application/json')


@allow_lazy_user
def block_tag(request, tag_name):
    '''
    Remove a tag for a user.
    '''
    tag = get_object_or_404(Tag, name=tag_name)
    TagBlock.objects.get_or_create(tag=tag, user=request.user)

    redirect_url = request.META['HTTP_REFERER'] or '/'
    return HttpResponseRedirect(redirect_url)    


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
