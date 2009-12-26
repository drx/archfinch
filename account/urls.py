from django.conf.urls.defaults import *

urlpatterns = patterns('hive.account.views',

    (r'^signup$', 'signup'),
    # (r'^login$', 'login'),
    # (r'^logout$', 'logout'),
    # (r'^prefs$', 'preferences'),
)

