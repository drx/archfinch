from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from main.models import Opinion

def overview(request, username):
    u = get_object_or_404(User, username=username)
    #opinions = u.opinion_set.order_by('item__category').all()
    print type(u.id)
    opinions = Opinion.objects.opinions_of(u.id, 1)
    return render_to_response('user/overview.html', {'user': u, 'opinions': opinions})
