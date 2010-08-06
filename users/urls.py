from django.conf.urls.defaults import *

urlpatterns = patterns('users.views',
    url(r'^(?P<username>[\w@\+\.-]+)$', 'overview', name='user-overview-simple'),
    url(r'^(?P<username>[\w@\+\.-]+)/(?P<category_slug>[\w-]*)$', 'overview', name='user-overview-slugged'),
    url(r'^(?P<username>[\w@\+\.-]+)/(?P<category_slug>[\w-]*)/(?P<start>\d+)/(?P<n>\d+)$', 'overview', name='user-overview-paged'),
)
