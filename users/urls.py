from django.conf.urls.defaults import *

urlpatterns = patterns('archfinch.users.views',
    url(r'^(?P<username>[\w@\+\.-]+)$', 'overview', name='user-overview'),

    url(r'^(?P<username>[\w@\+\.-]+)/review/(?P<item_id>[0-9a-z]+)(?:/(.*))?', 'review_show', name='review'),
    url(r'^review/(?P<item_id>[0-9a-z]+)/edit$', 'review_edit', name='review-edit'),

    url(r'^(?P<username>[\w@\+\.-]+)/reviews$', 'reviews', name='user-reviews'),
    url(r'^(?P<username>[\w@\+\.-]+)/reviews/(?P<start>\d+)/(?P<n>\d+)$', 'reviews', name='user-reviews-paged'),


    url(r'^(?P<username>[\w@\+\.-]+)/(?P<category_slug>[\w-]+)$', 'overview', name='user-overview-slugged'),
    url(r'^(?P<username>[\w@\+\.-]+)/(?P<start>\d+)/(?P<n>\d+)$', 'overview', name='user-overview-paged'),
    url(r'^(?P<username>[\w@\+\.-]+)/(?P<category_slug>[\w-]+)/(?P<start>\d+)/(?P<n>\d+)$', 'overview', name='user-overview-slugged-paged'),

)
