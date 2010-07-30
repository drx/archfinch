from django.conf.urls.defaults import *


urlpatterns = patterns('hive.wiki.views',
    url(r'^edit/item/(?P<item_id>\d+)$', 'edit', name='wiki-edit-item'),
)
