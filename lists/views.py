from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.http import int_to_base36, base36_to_int
from django.db import transaction
from django.db.models import Max
from django.utils import simplejson
from archfinch.main.models import Item, Opinion
from archfinch.lists.models import List, Entry


def forbidden(request):
    resp = render_to_response('403.html', context_instance=RequestContext(request))
    resp.status_code = 403
    return resp


def view(request, list_id):
    list_id = base36_to_int(list_id)
    list = get_object_or_404(List, pk=list_id)
    if request.user.is_authenticated():
        entries = list.entries.all().extra(
            select={'your_rating': 'SELECT COALESCE((SELECT rating FROM main_opinion mo WHERE mo.user_id=%s AND mo.item_id=lists_entry.item_id))'},
            select_params=[request.user.id])
    else:
        entries = list.entries.all()

    if request.user.is_authenticated():
        try:
            opinion = request.user.opinion_set.get(item=list)
        except Opinion.DoesNotExist:
            opinion = None
    else:
        opinion = None

    return render_to_response('lists/view.html', locals(), context_instance=RequestContext(request))


def add(request, list_id, item_id):
    item_id = base36_to_int(item_id)
    item = get_object_or_404(Item, pk=item_id)

    if list_id == '!ignored':
        list, created = List.objects.get_or_create(owner=request.user, ignored=True, defaults={'category_id': 8, 'name': "{username}'s ignore list".format(username=request.user.username), 'options': {}})
        list_id = list.id
    elif list_id == '!queue':
        list, created = List.objects.get_or_create(owner=request.user, queue=True, defaults={'category_id': 8, 'name': "{username}'s queue".format(username=request.user.username), 'options': {}})
        list_id = list.id
    else:
        list_id = base36_to_int(list_id)
        list = get_object_or_404(List, pk=list_id, owner=request.user)

    order_max = list.entries.aggregate(Max('order'))['order__max']
    if order_max is None:
        order = 0
    else:
        order = order_max + 1

    list.entries.create(type=Entry.types['item'], item_id=item_id, order=order)
    
    data = {'success': True}
    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')


@transaction.commit_on_success
def save(request):
    data = {'success': True}
    if request.method == 'POST':
        list_id = base36_to_int(request.POST['list_id'])
        list = get_object_or_404(List, pk=list_id, owner=request.user)    

        name = request.POST['title']
        if list.name != name:
            list.name = name
            list.save()
        Entry.objects.filter(list=list).delete()

        i = 0
        for input_entry in request.POST.getlist('a'):
            if input_entry.startswith('heading_'):
                text = input_entry.partition('heading_')[2]
                list.entries.create(type=Entry.types['heading'], text=text, order=i)
            elif input_entry.startswith('item_'):
                item_data = input_entry.partition('item_')[2]
                item_id, sep, text = item_data.partition('_')
                item_id = base36_to_int(item_id)
                list.entries.create(type=Entry.types['item'], item_id=item_id, text=text, order=i)
            elif input_entry.startswith('text_'):
                text = input_entry.partition('text_')[2]
                list.entries.create(type=Entry.types['text'], text=text, order=i)

            i = i+1

        data['success'] = True

    else:
        #data['error_msg'] = 'Wrong request method'
        raise SuspiciousOperation('Wrong request method')

    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')
    

@login_required
def create(request):
    name = request.POST['name']
    list = request.user.list_set.create(category_id=8, name=name, options={})
        
    redirect_url = reverse('list-edit', args=[int_to_base36(list.id)])
    return HttpResponseRedirect(redirect_url)


def overview(request):
    if request.user.is_authenticated():
        your_lists = request.user.list_set.all()
        for e_list in your_lists:
            e_list.n = e_list.entries.filter(type=Entry.types['item']).count()
        recommended = request.user.recommend(category_id=8)  # get recommended lists
        recommended = list(recommended)
        for e_list in recommended:
            e_list.n = 0
            e_list.n = e_list.list.entries.filter(type=Entry.types['item']).count()
    return render_to_response('lists/overview.html', locals(), context_instance=RequestContext(request))


def edit(request, list_id):
    list_id = base36_to_int(list_id)
    list = get_object_or_404(List, pk=list_id)

    if list.owner != request.user:
        return forbidden(request)

    return render_to_response('lists/edit.html', locals(), context_instance=RequestContext(request))
