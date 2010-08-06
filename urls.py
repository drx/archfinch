from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',     'main.views.welcome'),
    url(r'^missing$', 'main.views.missing', name='missing'),

    url(r'^similar$', 'users.views.similar', name='similar'),
    url(r'^similar/(?P<start>\d+)/(?P<n>\d+)$', 'users.views.similar', name='similar-paged'),
    url(r'^recommend$', 'main.views.recommend', name='recommend'),
    url(r'^recommend/(?P<category_slug>[\w-]*)$', 'main.views.recommend', name='recommend-slugged'),
    url(r'^recommend/(?P<category_slug>[\w-]*)/(?P<start>\d+)/(?P<n>\d+)$', 'main.views.recommend', name='recommend-paged'),

    (r'^account/', include('account.urls')),
    (r'^wiki/', include('wiki.urls')),
    (r'^user/', include('users.urls')),

    url(r'^item/(?P<item_id>[0-9a-z]+)(?:/(.*))?$', 'main.views.item', name='item'),
    (r'^opinion/set/(?P<item_id>[0-9a-z]+)/(?P<rating>[1-5])$', 'main.views.opinion_set'),
    (r'^opinion/remove/(?P<item_id>[0-9a-z]+)$', 'main.views.opinion_remove'),

    (r'^search$', 'search.views.query'),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)
