from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^hive/', include('hive.foo.urls')),

    (r'^user/', include('hive.userprofiles.urls')),

    # (r'^account/login$', 'hive.accounts.login'),
    # (r'^account/logout$', 'hive.accounts.logout'),
    # (r'^account/prefs$', 'hive.accounts.preferences'),


    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
