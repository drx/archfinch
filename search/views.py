from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Count, Q
from main.models import Item, Category
import re


def query(request):
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

    results = Item.search.query(title).order_by('-opinion_count', '@weight')

    if 'in' in modifiers:
        cat_name = modifiers['in']
        category = Category.objects.get(
            Q(name__iexact=cat_name)|Q(element_singular__iexact=cat_name)|Q(element_plural__iexact=cat_name)|Q(slug__iexact=cat_name)
        )
        results = results.filter(category_id=category.id)

    if 'bang' in modifiers:
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

    count = results.count()

    categories = Category.objects.order_by('name').values_list('id', 'element_plural', 'slug')

    if request.user.is_authenticated():
        user_categories = request.user.categories()
    else:
        user_categories = set()
    
    #results = results.annotate(Count('opinion')).extra(
    #    select={'is_exact': "name ILIKE %s"},
    #    select_params=(title,)
    #    ).order_by('-is_exact', '-opinion__count', 'name')[start:start+n]

    results = results[start:start+n]

    left = count-(start+n)

    if request.user.is_authenticated():
        return render_to_response('search/results.html', locals(),
            context_instance=RequestContext(request))

    else:
        return render_to_response('search/results_anonymous.html',
            {'query': q, 'results': results},
            context_instance=RequestContext(request))
