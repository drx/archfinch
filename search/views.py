from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Count
from main.models import Item
import re


def query(request):
    query = request.GET['q']
    start = int(request.GET.get('s', 0))
    n = int(request.GET.get('n', 10))

    if not 0 < n <= 100:
        n = 10

    words = re.findall(r'([\w:]*?"[\w: ]+"[\w:]*?|[\w:]+)', query)
    words = map(lambda w: w.replace('"',''), words)

    results = Item.objects.all()
    for word in words:
        results = results.filter(name__icontains=word)

    count = results.count()
    results = results.annotate(Count('opinion')).order_by('-opinion__count', 'name')[start:start+n]

    left = count-(start+n)

    if request.user.is_authenticated():
        return render_to_response('search/results.html', locals(),
            context_instance=RequestContext(request))

    else:
        return render_to_response('search/results_anonymous.html',
            {'query': q, 'results': results},
            context_instance=RequestContext(request))
