from django.conf.urls.defaults import *

urlpatterns = patterns('hive.account.views',

    (r'^signup$', 'signup'),
    # (r'^login$', 'login'),
    # (r'^logout$', 'logout'),
    (r'^prefs$', 'preferences'),

    (r'^debug/updatesim$', 'update_similarities'),
)

urlpatterns += patterns('',
    (r'^login$', 'django.contrib.auth.views.login',
        {'template_name': 'account/login.html'}),
    (r'^logout$', 'django.contrib.auth.views.logout',
        {'template_name': 'account/logout.html'}),

)

