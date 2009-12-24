from django.conf.urls.defaults import *

urlpatterns = patterns('hive.userprofiles.views',

    (r'^(?P<username>[a-zA-Z_]+)$', 'overview'),
)

