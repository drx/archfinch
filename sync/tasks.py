import pycurl
import StringIO
from celery.decorators import task, periodic_task
from datetime import timedelta, datetime
import time
import urllib
from django.conf import settings
try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        raise ImportError("Need a json decoder")

from archfinch.main.models import Opinion
from archfinch.links.models import Link
from archfinch.users.models import User
from archfinch.sync.models import Synced, Source

def get_url(url, userpwd=None):
    content = StringIO.StringIO()
    curl = pycurl.Curl()

    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.USERAGENT, "Archfinch/1.0 (email luke@archfinch.com)")
    curl.setopt(pycurl.CONNECTTIMEOUT, 30)
    curl.setopt(pycurl.TIMEOUT, 300)
    curl.setopt(pycurl.WRITEFUNCTION, content.write)
    if userpwd is not None:
        curl.setopt(pycurl.USERPWD, userpwd)

    curl.perform()

    response = {}
    response['content'] = content.getvalue()
    response['http_code'] = curl.getinfo(pycurl.HTTP_CODE)

    time.sleep(1)

    return response


@periodic_task(run_every=timedelta(hours=1))
def sync_hn():
    page = None
    items = []

    for i in range(5):    
        url = "http://api.ihackernews.com/page"
        if page is not None:
            url += "/" + page
        response = get_url(url)

        if response['http_code'] != 200:
            break

        content = json.loads(response['content'])

        page = content['nextId']
        items += [item for item in content['items'] if item['points'] >= 10]

    item_ids = map(lambda item: str(item['id']), items)
    ids_to_exclude = Synced.objects.filter(original_id__in=item_ids).values_list('original_id', flat=True)

    items = filter(lambda item: str(item['id']) not in ids_to_exclude, items)

    archfinch_user = User.objects.get(username='archfinch')
    hn_source = Source.objects.get(name='Hacker News')

    for item in items:
        # change to get_or_create
        tags = ['hn']
        url = item['url']
        if not url.startswith('http://'):
            url = 'http://news.ycombinator.com/item?id=' + item['id']
            tags.append('askhn')
        try:
            link = Link.objects.get(url=url)
            created = False
        except Link.DoesNotExist:
            link = Link(url=url, name=item['title'])
            created = True

        if created:
            link.submitter = archfinch_user
            link.get_meta_data()
            link.save()

            t, sep, t_factor = item['postedAgo'].partition(' ')
            delta = None
            if t_factor == 'minutes ago':
                delta = timedelta(minutes=int(t))
            elif t_factor == 'hours ago':
                delta = timedelta(hours=int(t))
            elif t_factor == 'days ago':
                delta = timedelta(hours=int(t)*24)
            if delta:
                link.time -= delta
                link.save()

        synced = Synced(link=link, source=hn_source, original_id=str(item['id']))
        synced.save()

        if not created:
            if link.tags.exists():
                synced.scraped = True
                synced.save()

        for tag in tags:
            link.add_tag(tag, archfinch_user)
        Opinion.objects.create(user=archfinch_user, item_id=link.id, rating=4)

    scrape_tags()


def parse_tags(content):
    import re
    tags = re.findall('<popular>(.*?)</popular>', content)

    return tags


def scrape_tags():
    synced = Synced.objects.filter(scraped=False).order_by('-id')
    synced = synced[:400]

    archfinch_user = User.objects.get(username='archfinch')

    for synced_item in synced:
        try:
            synced_item.scrape_attempts += 1
            synced_item.save()

            params = {'url': synced_item.link.url}
            url = 'https://api.del.icio.us/v1/posts/suggest?' + urllib.urlencode(params)

            response = get_url(url, userpwd=settings.DELICIOUS_USERPWD)

            if response['http_code'] in (500, 999):
                break

            if response['http_code'] != 200:
                continue

            tags = parse_tags(response['content'])

            if tags:
                for tag in tags:
                    synced_item.link.add_tag(tag, archfinch_user)

                synced_item.scraped = True
                synced_item.save()

        except Exception as err:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning('%s: %s' % (err.__class__.__name__, err, params['url']))

            continue

    Synced.objects.filter(scraped=False).filter(scrape_attempts__gte=3).update(scraped=True)
