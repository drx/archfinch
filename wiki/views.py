from wiki.models import PageForm, Page, Revision, RevisionText
from main.models import Item
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect


def edit(request, page_id=None, item_id=None):
    '''
    Lets the user edit a wiki page.
    '''

    # get the page
    if page_id is None and item_id is None:
        from django.core.exceptions import SuspiciousOperation
        raise SuspiciousOperation('Page id and item id were both empty')

    if page_id is None:
        item = get_object_or_404(Item, pk=int(item_id))
        page = item.profile.page
        redirect_url = reverse('item', args=[item_id])
    else:
        page = get_object_or_404(Page, pk=int(page_id))
        redirect_url = reverse('wiki-page', args=[page_id])

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if page is None:
                page = Page()
                page.save()
                item.profile.page = page
                item.profile.save()

            text = form.cleaned_data['text']
            revision_text = RevisionText(text=text)
            revision_text.save()

            page.revisions.create(text=revision_text, user=request.user)
            
            return HttpResponseRedirect(redirect_url)
    else:
        if page is not None:
            text = page.current().text.render()
        else:
            text = ''
        form = PageForm(initial={'text': text})

    return render_to_response('wiki/edit.html', locals(), context_instance=RequestContext(request))

