from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.db.models import Count, Q
from djangosphinx.apis import current as djangosphinx_api
from djangosphinx.models import SearchError
from django.utils import simplejson
from django.conf import settings
from archfinch.utils import render_to_response
from archfinch.main.models import Item, Category, Tag
from archfinch.users.models import User
from lazysignup.decorators import allow_lazy_user
from archfinch.utils import paginate
import re


@allow_lazy_user
def query(request, query=None, page=None, json=False, autocomplete=False):
    def invalid_search():
        if json:
            return render_to_response('search/invalid.json', locals(), context_instance=RequestContext(request), mimetype='application/json')
        else:
            return render_to_response('search/invalid.html', locals(), context_instance=RequestContext(request))

    if 'q' in request.GET:
        query = request.GET['q']

    if page is None:
        page = 1
    else:
        page = int(page)
    n = 10

    modifiers = {'tag': []}
    words = query.split()

    if autocomplete:
        json = True

    if len(words) > 1 and words[0] == '!':
        modifiers['bang'] = True
        words = words[1:]

    words_cleaned = []
    for word in words:
        mod, colon, arg = word.partition(':')
        if not colon:
            words_cleaned.append(word)
            continue

        if mod == 'in':
            modifiers['in'] = arg

        elif mod == 'tag':
            modifiers['tag'].append(arg)

        else:
            words_cleaned.append(word)

    words = words_cleaned
    title = ' '.join(words)

    results = Item.search.query(title).order_by('-opinion_count', '@weight').select_related('category')
    if request.user.is_authenticated() and not json:
        results = results.extra(
            select={'rating': 'SELECT COALESCE((SELECT rating FROM main_opinion mo WHERE mo.user_id=%s AND mo.item_id=main_item.id))'},
            select_params=[request.user.id])

    tags = Tag.objects.filter(name__in=modifiers['tag'])
    for tag in tags:
        results = results.filter(tag=tag.id)     

    results_pre_categories = results
    if 'in' in modifiers:
        cat_name = modifiers['in']
        try:
            category = Category.objects.get(
                Q(name__iexact=cat_name)|Q(element_singular__iexact=cat_name)|Q(element_plural__iexact=cat_name)|Q(slug__iexact=cat_name)
            )
            results = results.filter(category_id=category.id)
        except Category.DoesNotExist:
            return invalid_search()

    if 'bang' in modifiers and not json:
        try:
            result = results[0]
            from django.shortcuts import redirect
            from django.utils.http import int_to_base36
            from django.core.urlresolvers import reverse
            from django.template.defaultfilters import slugify
            return redirect(result.get_absolute_url())
        except IndexError:
            from django.http import Http404
            raise Http404
        except SearchError:
            return invalid_search()

    results_categories = results_pre_categories.group_by('category_id', djangosphinx_api.SPH_GROUPBY_ATTR)
    cats = map(lambda x: x._sphinx['attrs']['@groupby'], results_categories)
    categories = Category.objects.in_bulk(cats)

    category_counts = []
    for r in results_categories:
        cat_id = r._sphinx['attrs']['@groupby']
        cat_count = r._sphinx['attrs']['@count']
        category_counts.append({'category': categories[cat_id], 'count': cat_count})

    category_counts.sort(key=lambda x: x['count'], reverse=True)

    try:
        count = results.count()
    except SearchError:
        return invalid_search()

    results, paginator, current_page, page_range = paginate(results, page, n)

    if json:
        if autocomplete:
            for result in results:
                result.highlighted_name = result.name
        return render_to_response('search/results.json', locals(), context_instance=RequestContext(request), mimetype='application/json')
    else:
        return render_to_response('search/results.html', locals(), context_instance=RequestContext(request))


def user_search(request):
    query = request.GET['term']
  
    if settings.DEBUG:
        # some quirky bug in the devserver
        users = User.objects.filter(username__contains=query)
    else:
        users = User.objects.filter(username__icontains=query)

    users = users[:10].values_list('username', flat=True)
 
    json = simplejson.dumps(map(str,users))
    return HttpResponse(json, mimetype='application/json')
