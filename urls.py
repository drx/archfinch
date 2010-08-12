from django.conf.urls.defaults import *
from archfinch import site

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',     'archfinch.main.views.welcome'),
    url(r'^missing$', 'archfinch.main.views.missing', name='missing'),

    url(r'^similar$', 'archfinch.users.views.similar', name='similar'),
    url(r'^similar/(?P<start>\d+)/(?P<n>\d+)$', 'archfinch.users.views.similar', name='similar-paged'),
    url(r'^recommend$', 'archfinch.main.views.recommend', name='recommend'),
    url(r'^recommend/(?P<category_slug>[\w-]+)$', 'archfinch.main.views.recommend', name='recommend-slugged'),
    url(r'^recommend/(?P<start>\d+)/(?P<n>\d+)$', 'archfinch.main.views.recommend', name='recommend-paged'),
    url(r'^recommend/(?P<category_slug>[\w-]+)/(?P<start>\d+)/(?P<n>\d+)$', 'archfinch.main.views.recommend', name='recommend-slugged-paged'),
    
    (r'^account/', include('archfinch.account.urls')),
    (r'^wiki/', include('archfinch.wiki.urls')),
    (r'^user/', include('archfinch.users.urls')),

    url(r'^item/(?P<item_id>[0-9a-z]+)(?:/(.*))?$', 'archfinch.main.views.item', name='item'),
    (r'^opinion/set/(?P<item_id>[0-9a-z]+)/(?P<rating>[1-5])$', 'archfinch.main.views.opinion_set'),
    (r'^opinion/remove/(?P<item_id>[0-9a-z]+)$', 'archfinch.main.views.opinion_remove'),

    (r'^search$', 'archfinch.search.views.query'),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

 
if not site.production:
    urlpatterns += patterns('', 
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/django/archfinch/media'}),
        (r'^favicon.ico$', 'django.views.generic.simple.redirect_to', {'url': '/var/django/archfinch/media/favicon.ico', 'permanent': False}),
    )

