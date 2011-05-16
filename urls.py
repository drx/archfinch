from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',     'archfinch.main.views.recommend', {'category_slug': 'fresh'}),
    url(r'^missing$', 'archfinch.main.views.missing', name='missing'),
    url(r'^submit$', 'archfinch.links.views.submit', name='submit'),

    url(r'^similar$', 'archfinch.users.views.similar', name='similar'),
    url(r'^similar/(?P<page>\d+)$', 'archfinch.users.views.similar', name='similar-paged'),
    url(r'^recommend/fresh$', 'archfinch.main.views.recommend', {'category_slug': 'fresh'}, name='fresh'),
    url(r'^recommend$', 'archfinch.main.views.recommend', name='recommend'),
    url(r'^recommend/(?P<category_slug>[a-z-]+)$', 'archfinch.main.views.recommend', name='recommend-slugged'),
    url(r'^recommend/(?P<page>\d+)$', 'archfinch.main.views.recommend', name='recommend-paged'),
    url(r'^recommend/(?P<category_slug>[a-z-]+)/(?P<page>\d+)$', 'archfinch.main.views.recommend', name='recommend-slugged-paged'),
    url(r'^recommend(?:/(?P<category_slug>[a-z-]*))?/for/(?P<usernames>[,\w@\+\.-]+)(?:/(?P<page>\d+))?$', 'archfinch.main.views.recommend', name='recommend-for'),

    url(r'task_wait/(?P<task_id>[\w-]+)$', 'archfinch.main.views.task_wait', name='task-wait'),
    url(r'task_wait_error$', 'archfinch.main.views.task_wait_error', name='task-wait-error'),
    
    (r'^account/', include('archfinch.account.urls')),
    (r'^wiki/', include('archfinch.wiki.urls')),
    (r'^comment/', include('archfinch.comments.urls')),
    (r'^user/', include('archfinch.users.urls')),
    url(r'^me$', 'archfinch.users.views.overview_me', name='user-overview-me'),
    (r'^list/', include('archfinch.lists.urls')),
    (r'^convert/', include('lazysignup.urls')),

    url(r'^topusers$', 'archfinch.users.views.top_users', name='top-users'),

    url(r'^lists$', 'archfinch.lists.views.overview', name='lists-overview'),
    url(r'^lists/user/(?P<username>[\w@\+\.-]+)$', 'archfinch.lists.views.user', name='lists-user'),
    url(r'^utils/markdown$', 'archfinch.main.views.process_markdown', name='utils-markdown'),

    url(r'^item/(?P<item_id>[0-9a-z]+)(?:/(.*))?$', 'archfinch.main.views.item', name='item'),
    (r'^also_liked/(?P<item_id>[0-9a-z]+)/(?P<like>true|false)/(?P<also_like>true|false)$', 'archfinch.main.views.item_also_liked'),
    (r'^opinion/set/(?P<item_id>[0-9a-z]+)/(?P<rating>[1-5])$', 'archfinch.main.views.opinion_set'),
    (r'^opinion/remove/(?P<item_id>[0-9a-z]+)$', 'archfinch.main.views.opinion_remove'),

    url(r'tags/(?P<tag_names>.+)/(?P<page>\d+)$', 'archfinch.main.views.recommend', name='fresh-tags-paged'),
    url(r'tags/(?P<tag_names>.+)', 'archfinch.main.views.recommend', name='fresh-tags'),
    (r'^addtag/(?P<item_id>[0-9a-z]+)$', 'archfinch.main.views.add_tag'),
    url(r'^blocktag/(?P<tag_name>[^\/]+)$', 'archfinch.main.views.block_tag', name='block-tag'),
    url(r'^followtag/(?P<tag_name>[^\/]+)$', 'archfinch.main.views.follow_tag', name='follow-tag'),

    url(r'^search$', 'archfinch.search.views.query', {'query': ''}, name='search-base'),
    url(r'^search/(?P<query>.*?)(?:/(?P<page>\d+))?(?P<json>\.json)?(?P<autocomplete>\.autocomplete)?$', 'archfinch.search.views.query', name='search'),
    url(r'^usersearch$', 'archfinch.search.views.user_search', name='user-search'),
    url(r'^tagsearch$', 'archfinch.search.views.tag_search', name='tag-search'),

    url(r'^ref/(?P<username>[\w@\+\.-]+)$', 'archfinch.users.views.referral', name='referral'),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/django/archfinch/media'}),
        (r'^favicon.ico$', 'django.views.generic.simple.redirect_to', {'url': '/var/django/archfinch/media/favicon.ico', 'permanent': False}),
    )

