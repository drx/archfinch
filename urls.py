from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',     'hive.main.views.welcome'),
    (r'^user/', include('hive.users.urls')),
    (r'^similar', 'hive.users.views.similar'),
    (r'^recommend', 'hive.main.views.recommend'),
    (r'^account/', include('hive.account.urls')),
    (r'^test/', include('hive.testdata.urls')),

    (r'^item/(?P<item_id>[0-9]+)(?:/(.*))?$', 'hive.main.views.item'),
    (r'^opinion/set/(?P<item_id>[0-9]+)/(?P<rating>[1-5])$',
        'hive.main.views.opinion_set'),
    (r'^opinion/remove/(?P<item_id>[0-9]+)$',
        'hive.main.views.opinion_remove'),

    (r'^search$', 'hive.search.views.query'),

    # TEMPORARY, FOR DEVELOPMENT ONLY
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/drx/hive/media'}),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)
