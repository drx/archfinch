from django.db import models
from djangosphinx.models import SphinxSearch


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    element_singular = models.CharField(max_length=200)
    element_plural = models.CharField(max_length=200)

    # hide subclasses and other unwanted categories
    hide = models.BooleanField()

    def __unicode__(self):
        return self.name


class ItemManager(models.Manager):
    def recommended(self, users, category=None, category_id=None):
        '''
        Fetches items recommended for the user (which the user has not already rated)
         and returns an iterator.

        The algorithm should cut off at a certain amount of similar users,
         as potentially it's millions of similar users.
        '''
        from itertools import takewhile

        where = ''
        params = [tuple(map(lambda u: u.id, users))]*4
        if category is not None and category:
            category_id = category.id

        if category_id is not None:
            where += ' AND mi.category_id = %s'
            params.append(category_id)
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
        recommended = Item.objects.raw("""
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
            WHERE ms.user1_id IN %s
             AND ms.user2_id NOT IN %s
             AND ms.value > 0
             AND NOT EXISTS
              (SELECT 1 FROM main_opinion mo2
               WHERE mo2.item_id=mi.id AND mo2.user_id IN %s)
             AND NOT EXISTS
              (SELECT 1 FROM lists_list ll JOIN lists_entry le ON ll.item_ptr_id=le.list_id WHERE ll.owner_id IN %s AND le.item_id=mi.id)
             """+where+"""
            GROUP BY mi.id, mi.category_id, mi.parent_id, mi.name, category_element
            ORDER BY recommendation DESC) AS recommended WHERE recommendation > 0""",
            params)

        return recommended



class Item(models.Model):
    category = models.ForeignKey(Category)
    parent = models.ForeignKey('Item', null=True, blank=True)
    name = models.CharField(max_length=1000)

    submitter = models.ForeignKey('users.User', null=True, blank=True)

    search = SphinxSearch(
        mode='SPH_MATCH_EXTENDED2',
        rankmode='SPH_RANK_SPH04',
        weights={'name': 1},
        index='main_item',
    )

    objects = ItemManager()

    def __unicode__(self):
        return self.name

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

    def also_liked(self, user=None, category=None, category_id=None, like=True, also_like=True):
        '''
        Fetches items (dis)liked by users who (dis)like a given item for the user (which the user has not already rated)
         and returns an iterator.
        '''
        from itertools import takewhile

        params = [self.id, self.id]
        select = ''
        where = ''
        if category is not None and category:
            category_id = category.id

        if category_id is not None:
            where += ' AND mi.category_id = %s'
            params.append(category_id)
        else:
            where += " AND mc.hide = 'f'"

        if like:
            where += " AND mo2.rating >= 4"
        else:
            where += " AND mo2.rating <= 2"

        if user is not None:
            select += ', COALESCE((SELECT rating FROM main_opinion mo WHERE mo.user_id=%s AND mo.item_id=mi.id)) as rating' % (user.id)

        recommended = Item.objects.raw("""
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
            LIMIT 10""",
            params)

        return recommended


class ItemProfile(models.Model):
    item = models.OneToOneField(Item, related_name='profile')

    page = models.ForeignKey('wiki.Page', null=True)


class Review(models.Model):
    item = models.ForeignKey(Item)
    user = models.ForeignKey('users.User')
    text = models.TextField()


class Action(models.Model):
    time = models.DateTimeField(auto_now=True, unique=False)
    opinion = models.ForeignKey('Opinion', null=True, blank=True)
    review = models.ForeignKey('Review', null=True, blank=True)
    user = models.ForeignKey('users.User')

    types = {
        'rating': 1,
        'review': 2,
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

    def __unicode__(self):
        return "S(%s, %s) = %d" % (self.user1.username,
            self.user2.username, self.value)
