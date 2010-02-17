from django.conf.urls.defaults import *

urlpatterns = patterns('hive.userprofiles.views',

    (r'^(?P<username>[a-zA-Z0-9_]+)$', 'overview'),
)

