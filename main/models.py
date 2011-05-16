from django.db import models
from django.db.models import Count
from djangosphinx.models import SphinxSearch
from django.db.models.signals import post_save
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    element_singular = models.CharField(max_length=200)
    element_plural = models.CharField(max_length=200)

    # hide subclasses and other unwanted categories
    hide = models.BooleanField(db_index=True)

    def __unicode__(self):
        return self.name


class SlicedRawQuerySet(object):
    def __init__(self, raw_query, model=None, params=None, using=None):
        self.raw_query = raw_query
        self.model = model
        self._db = using
        self.params = params or ()
        
    def __repr__(self):
        return "<SlicedRawQuerySet: %r>" % (self.raw_query % self.params)

    def __getitem__(self, k):
        if not isinstance(k, (slice, int, long)):
            raise TypeError 
        if isinstance(k, slice):
            start = k.start or 0
            limit = str(k.stop-start) or 'NULL'
            query = "SELECT * FROM (%s) as raw LIMIT %s OFFSET %d" % (self.raw_query, limit, start)
            rawqueryset = models.query.RawQuerySet(raw_query=query, model=self.model, params=self.params, using=self._db)
            return list(rawqueryset)
        else:
            return self[k:k+1][0]

    def __len__(self):
        return self.count()

    def count(self):
        from django.db import connection, transaction
        cursor = connection.cursor()
        query = "SELECT COUNT(1) FROM (%s) as raw" % (self.raw_query)
        cursor.execute(query, self.params)
        row = cursor.fetchone()

        return row[0]
        

class SlicedRawManager(models.Manager):
    def slicedraw(self, raw_query, params=None, *args, **kwargs):
        return SlicedRawQuerySet(raw_query=raw_query, model=self.model, params=params, using=self._db, *args, **kwargs) 


class ItemManager(SlicedRawManager):
    def recommended_generic(self, category=None):
        '''
        Fetches items recommended generally (i.e. not for a specific user).
        '''
        params = {}
        where = ''
        if category is not None:
            where += ' mi.category_id = %(category_id)s'
            params['category_id'] = category.id
        else:
            where += " mc.hide = 'f'"

        recommended = Item.objects.raw("""
            SELECT * FROM (SELECT mi.id, mi.category_id, mi.parent_id, mi.name,
             SUM((mo.rating-3)) AS recommendation,
             mc.element_singular AS category_element
            FROM main_opinion mo
             INNER JOIN main_item mi
              ON mo.item_id=mi.id
             INNER JOIN main_category mc
              ON mc.id=mi.category_id
            WHERE 
             """+where+"""
            GROUP BY mi.id, mi.category_id, mi.parent_id, mi.name, category_element
            ORDER BY recommendation DESC) AS recommended WHERE recommendation > 0""",
            params)

        return recommended

    def recommended(self, users, category=None, category_id=None):
        '''
        Fetches items recommended for the user (which the user has not already rated)
         and returns an iterator.

        The algorithm should cut off at a certain amount of similar users,
         as potentially it's millions of similar users.
        '''
        from itertools import takewhile

        user_ids = map(lambda u: u.id, users)

        where = ''
        params = {'user_ids': tuple(user_ids)}
        if category is not None and category:
            category_id = category.id

        if category_id is not None:
            where += ' AND mi.category_id = %(category_id)s'
            params['category_id'] = category_id
        else:
            where += " AND mc.hide = 'f'"

        # Select items in order of their recommendation to self
        # 
        # recommendation =
        #    sum (rating-3)*similarity for all similar users
        # 
        #    where 
        #      rating: what the user has rated the item
        #      similarity: similarity between the user and self
        recommended = Item.objects.draw("""
            SELECT * FROM (SELECT mi.id, mi.category_id, mi.parent_id, mi.name,
             SUM((mo.rating-3)*ms.value) AS recommendation,
             mc.element_singular AS category_element
            FROM main_similarity ms
             INNER JOIN main_opinion mo
              ON ms.user2_id=mo.user_id
             INNER JOIN main_item mi
              ON mo.item_id=mi.id
             INNER JOIN main_category mc
              ON mc.id=mi.category_id
            WHERE ms.user1_id IN %(user_ids)s
             AND ms.user2_id NOT IN %(user_ids)s
             AND ms.value > 0
             AND NOT EXISTS
              (SELECT 1 FROM main_opinion mo2
               WHERE mo2.item_id=mi.id AND mo2.user_id IN %(user_ids)s)
             AND NOT EXISTS
              (SELECT 1 FROM lists_list ll JOIN lists_entry le ON ll.item_ptr_id=le.list_id WHERE ll.owner_id IN %(user_ids)s AND le.item_id=mi.id)
             AND NOT EXISTS 
              (SELECT 1 FROM main_tagblock mtb, main_tagged mtgd WHERE mtgd.tag_id=mtb.tag_id AND mtb.user_id IN %(user_ids)s AND mtgd.item_id=mi.id)
             """+where+"""
            GROUP BY mi.id, mi.category_id, mi.parent_id, mi.name, category_element
            ORDER BY recommendation DESC) AS recommended WHERE recommendation > 0""",
            params)

        return recommended



class Item(models.Model):
    category = models.ForeignKey(Category)
    parent = models.ForeignKey('Item', related_name='children', null=True, blank=True)
    name = models.CharField(max_length=1000, null=True, blank=True)

    submitter = models.ForeignKey('users.User', null=True, blank=True)
    tags = models.ManyToManyField('Tag', through='Tagged')

    search = SphinxSearch(
        mode='SPH_MATCH_EXTENDED2',
        rankmode='SPH_RANK_SPH04',
        weights={'name': 1},
        index='main_item',
    )

    objects = ItemManager()

    def __unicode__(self):
        if self.is_comment():
            return self.comment.__unicode__()
        else:
            return self.name

    @models.permalink
    def get_absolute_url(self):
        from django.utils.http import int_to_base36
        from django.template.defaultfilters import slugify
        slug = slugify(self.__unicode__())
        if self.is_comment():
            slug += '#topcomment'
        url = ('item', (int_to_base36(self.id), slug))
        return url 

    def get_meta_data(self):
        from django.core.exceptions import ObjectDoesNotExist
        from archfinch.links.scraper import scrape, generate_thumbnail

        if self.__class__.__name__ == 'Link':
            scraped_data = scrape(self.url)
            self.category_id = scraped_data['category_id']
            if 'thumbnail_url' in scraped_data:
                self.thumbnail = {'url': scraped_data['thumbnail_url'], 'width': scraped_data['thumbnail_width'], 'height': scraped_data['thumbnail_height']}
            if 'url' in scraped_data:
                self.image = {'url': scraped_data['url'], 'width': scraped_data['width'], 'height': scraped_data['height']}
            if 'html' in scraped_data:
                self.html = scraped_data['html']
            if scraped_data['category'] == 'pic':
                generate_thumbnail(self)
                    
        self.save()
        item_profile = ItemProfile(item=self)
        item_profile.save()
        self.profile = item_profile
        self.save()
        if scraped_data['category'] in ('pic', 'video'):
            if scraped_data['category'] == 'pic':
                tag = 'pics'
            else:
                tag = 'videos'
            archfinch_user = models.get_model('users', 'user').objects.get(username='archfinch')
            self.add_tag(tag, archfinch_user)
        

    def post_save_message(self, created):
        if created:
            return '%s has just %s %s' % (self.submitter, self.post_save_verb, self.__unicode__())
        else:
            return None
    post_save_verb = 'submitted'
    post_save_public = True

    def recommendation(self, user):
        '''
        Returns the recommendation value for an item for the user.

        Please take extra care to ensure the algorithm is the same as in User.recommend.
        '''
        items = Item.objects.raw("""
            SELECT mi.id, SUM((mo.rating-3)*ms.value) AS recommendation
            FROM main_similarity ms
             INNER JOIN main_opinion mo
              ON ms.user2_id=mo.user_id
             INNER JOIN main_item mi
              ON mo.item_id=mi.id
            WHERE ms.user1_id=%s
             AND ms.user2_id!=%s
             AND ms.value > 0
             AND mi.id = %s
            GROUP BY mi.id
            """,
            [user.id, user.id, self.id])

        items = list(items)
        if items:
            return items[0].recommendation
        else:
            return 0

    def similar_by_tags(self):
        '''
        Fetches items with co-occuring tags, ordered by the number of co-occurences.
        '''
        popular_tags = self.popular_tags()
        if not popular_tags:
            return Item.objects.none()

        items = Item.objects.slicedraw("""
            SELECT item_id as id, similarity
            FROM (
              SELECT item_id, count(CASE WHEN tag_id in %(tag_ids)s THEN 1 ELSE NULL END) as similarity
              FROM main_tagged
              GROUP BY item_id
            ) AS related_items
            WHERE similarity > 0
             AND item_id != %(item_id)s
            ORDER BY similarity desc
            """,
            {'item_id': self.id, 'tag_ids': tuple(map(lambda x: x.id, popular_tags))})

        return items

    def also_liked(self, user=None, category=None, category_id=None, like=True, also_like=True):
        '''
        Fetches items (dis)liked by users who (dis)like a given item for the user (which the user has not already rated)
         and returns an iterator.
        '''
        from itertools import takewhile

        params = [self.id, self.id]
        select = ''
        where = ''

        # only show stuff for the same category as the element
        where += ' AND mi.category_id = %s'
        params.append(self.category.id)

        if like:
            where += " AND mo2.rating >= 4"
        else:
            where += " AND mo2.rating <= 2"

        if user is not None:
            select += ', COALESCE((SELECT rating FROM main_opinion mo WHERE mo.user_id=%s AND mo.item_id=mi.id)) as rating' % (user.id)

        recommended = Item.objects.slicedraw("""
            SELECT * FROM (
            SELECT mi.id, mi.category_id, mi.parent_id, mi.name,
             SUM(abs(mo2.rating-3)*(mo.rating-3)) AS recommendation,
             mc.element_singular AS category_element
             """+select+"""
            FROM main_opinion mo
             INNER JOIN main_opinion mo2
              ON mo.user_id=mo2.user_id
             INNER JOIN main_item mi
              ON mo.item_id=mi.id
             INNER JOIN main_category mc
              ON mc.id=mi.category_id
            WHERE mo2.item_id=%s
             AND mo.item_id!=%s
             """+where+"""
            GROUP BY mi.id, mi.category_id, mi.parent_id, mi.name, category_element
            ORDER BY recommendation DESC) AS recommended WHERE recommendation """+('>' if also_like else '<')+""" 0
            """,
            params)

        return recommended

    
    def root(self):
        params = {'item_id': self.id}

        return Item.objects.raw("""
            WITH RECURSIVE cte (id, parent_id, path) AS (
                (SELECT id, parent_id, array[id] FROM main_item WHERE id=%(item_id)s)
                UNION ALL
                SELECT mi.id, mi.parent_id, mi.id || cte.path FROM main_item mi JOIN cte ON cte.parent_id=mi.id
            )
            SELECT id, path FROM cte WHERE cte.parent_id IS NULL        
        """, params)[0]


    def comment_count(self):
        return self.comment_tree(count=True)


    def comment_tree(self, count=False, selected_path=None, user=None):
        params = {'root_id': self.id, 'selected_1': '', 'selected_n': ''}
        if count:
            order_by = ''
            select = 'COUNT(1)'
        else:
            order_by = 'ORDER BY path'
            select = 'id, parent_id, submitter_id, depth, cc.text'

        if user is not None:
            select += ', COALESCE((SELECT rating FROM main_opinion mo WHERE mo.user_id=%(user_id)s AND mo.item_id=cte.id)) AS rating'
            params['user_id'] = user.id

        if selected_path is not None:
            # I have a feeling someone, someday, will knife me for this
            params['selected_1'] = 'id!=%s, ' % selected_path[1]
            params['selected_n'] = 'c.id!=(array%s)[cte.depth+1], ' % selected_path[1:]

        
        query = """
            WITH RECURSIVE cte (id, parent_id, submitter_id, path, depth) AS (
                (SELECT id, parent_id, submitter_id, array[("""+params['selected_1']+""" 1-wilson_score(id), id)] as path, 1 FROM main_item WHERE parent_id=%(root_id)s)
                UNION ALL
                SELECT c.id, c.parent_id, c.submitter_id, cte.path || ("""+params['selected_n']+""" 1-wilson_score(c.id), c.id), cte.depth+1 FROM main_item c JOIN cte ON cte.id = c.parent_id
            )
            SELECT
                """+select+"""
            FROM cte
                INNER JOIN comments_comment cc ON cte.id=cc.item_ptr_id
            """+order_by+"""
            """

        if count:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()[0]

        comments = Item.objects.raw(query, params)

        # this is a bit more complicated than doing a sql query for each subtree
        #  but much much faster
        comment_tree = []
        last = None
        for comment in comments:
            if last is not None:
                diff = comment.depth - last
                if diff > 0:
                    comment_tree.extend([{'type': 'in'}]*diff)
                if diff < 0:
                    comment_tree.extend([{'type': 'out'}]*(-diff))
            comment_tree.append({'type': 'comment', 'comment': comment})
            last = comment.depth
        if last is not None:
            comment_tree.extend([{'type': 'out'}]*(last-1))

        return comment_tree


    def ratings_count(self):
        ratings_count = self.opinion_set.all().values('rating').annotate(count=Count('rating'))
        ratings_count = dict((x['rating'], x['count']) for x in ratings_count)
        for rating in range(1, 6):
            ratings_count.setdefault(rating, 0)

        import datetime
        if ratings_count and (not self.is_link() or self.link.time + datetime.timedelta(hours=6) < datetime.datetime.now()):
            # stuff rating counts (temporarily), but only for links that are 6 hours or older
            max_rating = max(ratings_count.values())
            for rating in range(1, 6):
                multiplier = 101 + self.id % 100 + 2*rating

                if ratings_count[rating] == 0:
                    ratings_count[rating] = multiplier*max_rating/97
                else:
                    ratings_count[rating] *= multiplier

        ratings_count = ratings_count.items()
        return ratings_count

    def submitter_show(self):
        submitter = self.submitter
        if not submitter:
            return None

        if submitter.username == 'archfinch':
            return None

        # if the submitter is drx, fake the user
        if submitter.id == 1:
            if not self.options.filter(option="showrealsubmitter").exists():
                new_id = self.id%128 + 100
                submitter = submitter.__class__.objects.get(id=new_id)

        return submitter


    def is_link(self):
        return self.category_id in (9,10,11)

    def is_comment(self):
        return self.category_id == 14
       

    def add_tag(self, tag_name, user):
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tagged, created = Tagged.objects.get_or_create(tag=tag, user=user, item=self)
        
        action, created = Action.objects.get_or_create(type=Action.types['tagged'], tagged=tagged, user=user)
        action.save()


    def popular_tags(self):
        return self.tags.annotate(Count('name')).order_by('name')[:6]


class ItemProfile(models.Model):
    item = models.OneToOneField(Item, related_name='profile')

    page = models.ForeignKey('wiki.Page', null=True)

class ItemOption(models.Model):
    item = models.ForeignKey(Item, related_name='options')

    option = models.CharField(max_length=50)


class TagManager(models.Manager):
    def related_tags(self, tags):
        params = {'tag_ids': tuple(map(lambda tag: tag.id, tags))}
        where = ''
        for tag in tags:
            where += ' AND EXISTS (SELECT 1 FROM main_tagged mtgd WHERE mtgd1.item_id = mtgd.item_id AND mtgd.tag_id = %d)' % (int(tag.id))
        return Tag.objects.raw("""
            SELECT mt.id, mt.name, count(1) as count
            FROM main_tagged mtgd1
             INNER JOIN main_tag mt
              ON mt.id=mtgd1.tag_id
            WHERE mtgd1.tag_id NOT IN %(tag_ids)s
             """+where+"""
            GROUP BY mt.id, mt.name
            HAVING count(1) >= 2
            ORDER BY count(1) DESC""", params)



class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)

    objects = TagManager()

    def __unicode__(self):
        return self.name


class Tagged(models.Model):
    item = models.ForeignKey(Item)
    tag = models.ForeignKey(Tag)
    user = models.ForeignKey('users.User')

    class Meta:
        unique_together = ('item', 'tag', 'user')

    def __unicode__(self):
        return '%s tagged %s with %s' % (self.user, self.item, self.tag)


class TagBlock(models.Model):
    tag = models.ForeignKey(Tag)
    user = models.ForeignKey('users.User')

    class Meta:
        unique_together = ('tag', 'user')

    def __unicode__(self):
        return '%s blocked %s' % (self.user, self.tag)


class Review(models.Model):
    item = models.ForeignKey(Item)
    user = models.ForeignKey('users.User')
    text = models.TextField()


class Action(models.Model):
    time = models.DateTimeField(auto_now=True, unique=False)
    opinion = models.ForeignKey('Opinion', null=True, blank=True)
    review = models.ForeignKey('Review', null=True, blank=True)
    tagged = models.ForeignKey('Tagged', null=True, blank=True)
    user = models.ForeignKey('users.User')

    types = {
        'rating': 1,
        'review': 2,
        'tagged': 3,
    }
    types_reverse = dict((v,k) for k, v in types.items())
    TYPE_CHOICES = types_reverse.items()
    type = models.IntegerField(choices=TYPE_CHOICES)

    def __unicode__(self):
        return self.time.ctime()


class Opinion(models.Model):
    user = models.ForeignKey('users.User')
    item = models.ForeignKey(Item)

    RATING_CHOICES = (
        (1, 'Hate it'),
        (2, 'Dislike it'),
        (3, 'Neutral to it'),
        (4, 'Like it'),
        (5, 'Love it'),
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, db_index=True)

    def __unicode__(self):
        return "%s gave %s a rating of %d." % (self.user.username, self.item.name, self.rating)

    def get_third_person(self):
        third_person_choices = {
            1: 'hates',
            2: 'dislikes',
            3: 'is neutral to',
            4: 'likes',
            5: 'loves',
            None: 'hasn\'t rated',
        }
        return third_person_choices[self.rating]


class SimilarityManager(models.Manager):
    def update_user(self, user):
        '''
        Update similarity values for a user against all other users.
        '''
        for user2 in User.objects.all():
            self.update_user_pair(user, user2)

    def update_item_delta(self, user, delta):
        '''
        Update similarity values for a user against all other users after
         an opinion set update, represented by a delta dict.
        '''
        from django.db import connection, transaction

        cursor = connection.cursor()

        items = list(delta.iterkeys())
        for item in items:
            cursor.execute("SELECT update_item_rated(%s, %s);", [user.id, item])

        transaction.commit_unless_managed()


    def update_user_pair(self, user1, user2):
        '''
        Update similarity values for a pair of users.

        NOTE: This has been superseded by update_item_delta.
         Never use this for production.
        '''
        from django.db import connection
        if user1 == user2:
            return

        cursor = connection.cursor()
        cursor.execute("""
            SELECT m1.rating, m2.rating
            FROM main_opinion m1
            INNER JOIN main_opinion m2
            ON (m1.item_id = m2.item_id AND m1.user_id=%s)
            WHERE m2.user_id = %s
            """, [user1.id, user2.id])

        value = 0
        for row in cursor.fetchall():
            difference = abs(row[0] - row[1])
            if difference == 0:
                value += 2
            elif difference == 1:
                value += 1
            elif difference == 2:
                pass
            elif difference == 3:
                value -= 1
            elif difference == 4:
                value -= 2
        obj, created = Similarity.objects.get_or_create(user1=user1,
            user2=user2, defaults={'value': value})
        if not created:
            obj.value = value
            obj.save()

        obj, created = Similarity.objects.get_or_create(user1=user2,
            user2=user1, defaults={'value': value})
        if not created:
            obj.value = value
            obj.save()


class Similarity(models.Model):
    user1 = models.ForeignKey('users.User')
    user2 = models.ForeignKey('users.User', related_name="similarity_set2")
    value = models.IntegerField(db_index=True)

    objects = SimilarityManager()

    class Meta:
        unique_together = ('user1', 'user2')

    def __unicode__(self):
        return "S(%s, %s) = %d" % (self.user1.username,
            self.user2.username, self.value)


def bot_post_save(sender, **kwargs):
    from archfinch.utils.bot import bot 
    instance = kwargs['instance']
    created = kwargs['created']

    try:
        message = instance.post_save_message(created)
        if message is None:
            return
        public = sender.post_save_public
    except AttributeError:
        return
        

    channels = ['#archfinch-log']
    if public:
        channels.append('#archfinch')

    try:
        path = instance.get_absolute_url()
        urlstr = ' (http://%s%s)' % (settings.DOMAIN, path)
    except AttributeError:
        urlstr = ''

    for channel in channels:
        bot.send_message(channel, '%s %s' % (message, urlstr))

post_save.connect(bot_post_save)

