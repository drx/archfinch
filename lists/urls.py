from django.conf.urls.defaults import *

urlpatterns = patterns('archfinch.lists.views',
    url(r'^edit/(?P<list_id>[0-9a-z]{1,13})$', 'edit', name='list-edit'),
    url(r'^delete/(?P<list_id>[0-9a-z]{1,13})$', 'delete', name='list-delete'),
    url(r'^save$', 'save', name='list-save'),
    url(r'^create$', 'create', name='list-create'),

    url(r'^to/(?P<list_id>[0-9a-z]{1,13}|!ignored|!queue)/add/(?P<item_id>[0-9a-z]{1,13})$', 'add', name='list-add'),
    
    url(r'^(?P<list_id>[0-9a-z]{1,13})(?:/(.*))?$', 'view', name='list-view'),

)
