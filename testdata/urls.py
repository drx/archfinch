from django.conf.urls.defaults import *

urlpatterns = patterns('hive.testdata.views',
    (r'^$', 'runtest'),
)
