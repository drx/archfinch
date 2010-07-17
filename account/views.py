from hive.account.models import SignupForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from main.models import Similarity
from django.contrib.auth import login as auth_login
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import AuthenticationForm
from django.utils import simplejson

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/")
    else:
        form = SignupForm()
    return render_to_response("account/signup.html",
        {'form': form},
        context_instance=RequestContext(request))

def logout_ajax(request):
    from django.contrib.auth import logout
    logout(request)

    json = simplejson.dumps({'success': True})
    return HttpResponse(json, mimetype='application/json')


@csrf_protect
@never_cache
def login_ajax(request):
    """Handles AJAX logins."""

    data = {'success': False}
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())

            data['success'] = True
            data['username'] = form.cleaned_data['username']

        else:
            data['error_msg'] = repr(form.errors)

    else:
        data['error_msg'] = 'Wrong request method'
    
    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')


def preferences(request):
    pass


def update_similarities(request):
    '''
    Update similarities against other users.

    This method is for debug purposes only, and should be removed as soon
     as it is not needed any more.
    '''

    if not request.user.is_authenticated():
        return HttpResponse('Log in first.')

    Similarity.objects.update_user(request.user)

    return HttpResponse('It is done.')
