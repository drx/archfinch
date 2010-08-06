from django.conf.urls.defaults import *


urlpatterns = patterns('archfinch.wiki.views',
    url(r'^edit/item/(?P<item_id>[0-9a-z]+)$', 'edit', name='wiki-edit-item'),
)
