from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import login as auth_login
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.utils import simplejson
from archfinch.utils import render_to_response, form_error_msg
from archfinch.main.models import Similarity
from archfinch.account.models import SignupForm, AuthenticationForm
from lazysignup.utils import is_lazy_user

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.backend = 'archfinch.users.auth_backends.ModelBackend'
            auth_login(request, new_user)

            return HttpResponseRedirect("/")
    else:
        form = SignupForm()
    return render_to_response("account/signup.html",
        {'form': form},
        context_instance=RequestContext(request))


def logout(request):
    if is_lazy_user(request.user):
        return render_to_response("account/logout.html", context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('loggedout'))


@csrf_protect
def signup_ajax(request):
    """Handles AJAX signups."""

    data = {'success': False}
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.backend = 'archfinch.users.auth_backends.ModelBackend'
            auth_login(request, new_user)

            data['success'] = True
            data['username'] = new_user.username

        else:
            data['error_msg'] = form_error_msg(form.errors)
    else:
        data['error_msg'] = 'Wrong request method'

    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')


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
            data['error_msg'] = form_error_msg(form.errors)

    else:
        data['error_msg'] = 'Wrong request method'
    
    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')


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
