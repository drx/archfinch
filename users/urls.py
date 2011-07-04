from django.conf.urls.defaults import *

urlpatterns = patterns('archfinch.users.views',
    url(r'^(?P<username>[\w@\+\.-]+)(?P<json>/json)?$', 'overview', name='user-overview'),

    url(r'^(?P<username>[\w@\+\.-]+)/review/(?P<item_id>[0-9a-z]{1,13})(?:/(.*))?', 'review_show', name='review'),
    url(r'^review/(?P<item_id>[0-9a-z]{1,13})/edit$', 'review_edit', name='review-edit'),

    url(r'^(?P<username>[\w@\+\.-]+)/reviews$', 'reviews', name='user-reviews'),
    url(r'^(?P<username>[\w@\+\.-]+)/reviews/(?P<page>\d+)$', 'reviews', name='user-reviews-paged'),


    url(r'^(?P<username>[\w@\+\.-]+)/(?P<category_slug>[a-z-]+)(?P<json>/json)?$', 'overview', name='user-overview-slugged'),
    url(r'^(?P<username>[\w@\+\.-]+)/(?P<page>\d+)(?P<json>/json)?$', 'overview', name='user-overview-paged'),
    url(r'^(?P<username>[\w@\+\.-]+)/(?P<category_slug>[a-z-]+)/(?P<page>\d+)(?P<json>/json)?$', 'overview', name='user-overview-slugged-paged'),

)
