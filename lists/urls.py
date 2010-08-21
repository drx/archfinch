from django.conf.urls.defaults import *

urlpatterns = patterns('archfinch.lists.views',
    url(r'^edit/(?P<list_id>[0-9a-z]+)$', 'edit', name='list-edit'),
    url(r'^save$', 'save', name='list-save'),
    url(r'^create$', 'create', name='list-create'),

    url(r'^to/(?P<list_id>[0-9a-z]+|!ignored|!queue)/add/(?P<item_id>[0-9a-z]+)$', 'add', name='list-add'),
    
    url(r'^(?P<list_id>[0-9a-z]+)(?:/(.*))?$', 'view', name='list-view'),

)
