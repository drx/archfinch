from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.db.models import Count, Q
from djangosphinx.apis import current as djangosphinx_api
from djangosphinx.models import SearchError
from django.utils import simplejson
from django.conf import settings
from archfinch.utils import render_to_response
from archfinch.main.models import Item, Category
from archfinch.users.models import User
from lazysignup.decorators import allow_lazy_user
import re


@allow_lazy_user
def query(request, json=False):
    def invalid_search():
        if json:
            return render_to_response('search/invalid.json', locals(), context_instance=RequestContext(request), mimetype='application/json')
        else:
            return render_to_response('search/invalid.html', locals(), context_instance=RequestContext(request))

    query = request.GET['q']
    start = int(request.GET.get('s', 0))
    n = int(request.GET.get('n', 10))

    if not 0 < n <= 100:
        n = 10

    modifiers = {}
    words = query.split()

    if len(words) > 1 and words[0] == '!':
        modifiers['bang'] = True
        words = words[1:]

    words_cleaned = []
    for word in words:
        mod, comma, arg = word.partition(':')
        if not comma:
            words_cleaned.append(word)
            continue

        if mod == 'in':
            modifiers['in'] = arg

        else:
            words_cleaned.append(word)

    words = words_cleaned
    title = ' '.join(words)

    results = Item.search.query(title).order_by('-opinion_count', '@weight').select_related('category')
    if request.user.is_authenticated() and not json:
        results = results.extra(
            select={'rating': 'SELECT COALESCE((SELECT rating FROM main_opinion mo WHERE mo.user_id=%s AND mo.item_id=main_item.id))'},
            select_params=[request.user.id])

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
            return redirect(reverse('item', args=[int_to_base36(result.id), slugify(result.name)]))
        except IndexError:
            from django.http import Http404
            raise Http404
        except SearchError:
            return invalid_search()

    try:
        count = results.count()
    except SearchError:
        return invalid_search()

    results_categories = Item.search.query(title).group_by('category_id', djangosphinx_api.SPH_GROUPBY_ATTR)
    cats = map(lambda x: x._sphinx['attrs']['@groupby'], results_categories)
    categories = Category.objects.in_bulk(cats)

    category_counts = []
    for r in results_categories:
        cat_id = r._sphinx['attrs']['@groupby']
        cat_count = r._sphinx['attrs']['@count']
        category_counts.append({'category': categories[cat_id], 'count': cat_count})

    category_counts.sort(key=lambda x: x['count'], reverse=True)
    
    results = results[start:start+n]

    left = count-(start+n)

    if json:
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
