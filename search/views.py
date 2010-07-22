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

    words = re.findall(r'([\w:]*?"[\w: ]+"[\w:]*?|[\w:]+)', query)
    words = map(lambda w: w.replace('"',''), words)

    modifiers = {}

    words_cleaned = []
    for word in words:
        mod, comma, arg = word.partition(':')
        if not comma:
            words_cleaned.append(word)
            continue

        if mod == 'in':
            modifiers['in'] = arg

        elif mod == 'exact':
            modifiers['exact'] = arg

        else:
            words_cleaned.append(word)

    words = words_cleaned
    title = ' '.join(words)

    results = Item.objects.all()

    for mod in modifiers:
        if mod == 'exact':
            results = results.filter(name__iexact=modifiers[mod])

        elif mod == 'in':
            cat_name = modifiers[mod]
            category = Category.objects.get(
                Q(name__iexact=cat_name)|Q(element_singular__iexact=cat_name)|Q(element_plural__iexact=cat_name)
            )
            results = results.filter(category=category)

    for word in words:
        results = results.filter(name__icontains=word)

    count = results.count()
    if request.user.is_authenticated():
        categories = set()
        for id, cat in request.user.categories():
            if ' ' in cat:
                link = '"'+cat+'"'
            else:
                link = cat
            categories.add((id, cat, link))

    else:
        categories = set()
    
    results = results.annotate(Count('opinion')).extra(
        select={'is_exact': "name ILIKE %s"},
        select_params=(title,)
        ).order_by('-is_exact', '-opinion__count', 'name')[start:start+n]

    left = count-(start+n)

    if request.user.is_authenticated():
        return render_to_response('search/results.html', locals(),
            context_instance=RequestContext(request))

    else:
        return render_to_response('search/results_anonymous.html',
            {'query': q, 'results': results},
            context_instance=RequestContext(request))
