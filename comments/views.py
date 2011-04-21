from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from archfinch.utils import render_to_response
from archfinch.comments.models import AddCommentForm
from archfinch.main.models import Item
from django.utils.http import base36_to_int

def add_comment(request):
    if request.method == 'POST':
        data = {'category': 14}
        data.update(request.POST.items())
        form = AddCommentForm(data)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.submitter = request.user
            comment.save()

            request.user.add_points(1)
            
            return HttpResponseRedirect(comment.get_absolute_url())

        else:
            return render_to_response('form_error.html', locals(), context_instance=RequestContext(request))
