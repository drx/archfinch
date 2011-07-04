from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.utils.http import base36_to_int
from django.utils import simplejson
from lazysignup.decorators import allow_lazy_user
from archfinch.utils import render_to_response, form_error_msg
from archfinch.comments.models import AddCommentForm
from archfinch.main.models import Item


@allow_lazy_user
def add_comment(request, json=False):
    if json:
        return_data = {'success': False}

    if request.method == 'POST':
        data = {'category': 14}
        data.update(request.POST.items())
        form = AddCommentForm(data)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.submitter = request.user
            comment.save()

            request.user.add_points(1)
            
            if json:
                return_data['success'] = True
                return_data['redirect_url'] = comment.get_absolute_url()
            else:
                return HttpResponseRedirect(comment.get_absolute_url())

        else:
            if json:
                return_data['error_msg'] = form_error_msg(form.errors)
            else:
                return render_to_response('form_error.html', locals(), context_instance=RequestContext(request))

    else:
        if json:
            return_data['error_msg'] = 'Wrong request method'
        else:
            return HttpResponseRedirect('/')

    if json:
        json = simplejson.dumps(return_data)
        return HttpResponse(json, mimetype='application/json')

