from django.conf.urls.defaults import *

urlpatterns = patterns('hive.users.views',
    (r'^(?P<username>[a-zA-Z0-9_]+)$', 'overview'),
)
