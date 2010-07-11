from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from main.models import Item
import re

def query(request):
    q = request.GET['q']

    words = re.findall(r'("[\w ]+"|\w+)', q)

    results = Item.objects.all()
    for word in words:
        if word.startswith('"'):
            word = word[1:-1]
        results = results.filter(name__icontains=word)

    if request.user.is_authenticated():
        return render_to_response('search/results.html',
            {'query': q, 'results': results},
            context_instance=RequestContext(request))

    else:
        return render_to_response('search/results_anonymous.html',
            {'query': q, 'results': results},
            context_instance=RequestContext(request))
