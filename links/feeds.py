from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib.syndication.views import Feed
from archfinch.main.views import recommend
from django.conf import settings
from django.core.urlresolvers import reverse

link_prefix = 'http://%s' % settings.DOMAIN


class LinkFeed(Feed):
    def get_object(self, request, **kwargs):
        obj = recommend(request, feed=True, **kwargs)
        obj['url'] = request.path_info.replace('/rss', '', 1)
        return obj

    def title(self, obj):
        if obj['followed']:
            desc = 'followed by %s' % obj['feed_username']
        elif obj['tags']:
            desc = ' + '.join(obj['tags'].values_list('name', flat=True))
        elif obj['category']:
            desc = obj['category'].element_singular
        else:
            desc = 'links'
            
        return "Archfinch.com: %s" % desc

    def item_description(self, item):
        return '<a href="%s">Comments</a>' % (link_prefix + item.get_absolute_url())

    def item_link(self, item):
        return item.url

    def link(self, obj):
        return obj['url']

    def description(self, obj):
        if obj['followed']:
            desc = 'Links in tags followed by %s on Archfinch' % obj['feed_username']
        elif obj['tags']:
            desc = 'Links tagged %s on Archfinch' % ' + '.join(obj['tags'].values_list('name', flat=True))
        else:
            desc = 'Links on Archfinch'
        return desc

    def items(self, obj):
        return obj['recommendations']
