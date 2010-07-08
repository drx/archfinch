from django.shortcuts import render_to_response
from django.template import RequestContext

def welcome(request):
    if request.user.is_authenticated():
        return render_to_response("main/welcome.html", context_instance=RequestContext(request))
    else:
        return render_to_response("main/welcome_anonymous.html", context_instance=RequestContext(request))
