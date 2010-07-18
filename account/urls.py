from django.conf.urls.defaults import *

urlpatterns = patterns('hive.account.views',

    (r'^signup$', 'signup'),
    # (r'^login$', 'login'),
    # (r'^logout$', 'logout'),
    (r'^prefs$', 'preferences'),

    url(r'^logout/ajax$', 'logout_ajax', name='logout-ajax'),
    url(r'^login/ajax$', 'login_ajax', name='login-ajax'),
    url(r'^signup/ajax$', 'signup_ajax', name='signup-ajax'),

    (r'^debug/updatesim$', 'update_similarities'),
)

urlpatterns += patterns('',
    url(r'^login$', 'django.contrib.auth.views.login',
        {'template_name': 'account/login.html'},
        name='login'),
    url(r'^logout$', 'django.contrib.auth.views.logout',
        {'template_name': 'account/logout.html'},
        name='logout'),
)
