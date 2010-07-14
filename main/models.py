from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=200)
    element_singular = models.CharField(max_length=200)
    element_plural = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category)
    parent = models.ForeignKey('Item', null=True, blank=True)
    name = models.CharField(max_length=1000)

    def __unicode__(self):
        return self.name


class ItemProfile(models.Model):
    item = models.OneToOneField(Item, related_name='profile')

    page = models.TextField()


class Action(models.Model):
    time = models.DateTimeField(auto_now_add=True, unique=False)

    def __unicode__(self):
        return self.time.ctime()


class OpinionManager(models.Manager):

    # get opinions of a user (viewed) on items that the viewer also rated
    def opinions_of(self, viewed, viewer):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT m1.id, m1.item_id, m1.rating, m2.rating
            FROM main_opinion m1
            LEFT JOIN main_opinion m2
            ON (m1.item_id=m2.item_id AND m2.user_id=%s)
            WHERE m1.user_id = %s
            ORDER BY m2.rating IS NULL, m1.rating DESC""",
                [viewer.id, viewed.id])  # Perhaps %d should be used here,
                                         #  instead of %s
        result_list = []
        for row in cursor.fetchall():
            p = self.model(id=row[0], item_id=row[1], rating=row[2])
            p.your_rating = row[3]
            result_list.append(p)
        return result_list


class Opinion(models.Model):
    user = models.ForeignKey(User)
    item = models.ForeignKey(Item)
    action = models.ForeignKey(Action, unique=True)

    RATING_CHOICES = (
        (1, 'Hate it'),
        (2, 'Dislike it'),
        (3, 'Neutral to it'),
        (4, 'Like it'),
        (5, 'Love it'),
        (6, 'Among my favorites'),
        (0, 'No opinion'),
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES,
        null=True, blank=True)

    objects = OpinionManager()

    def __unicode__(self):
        return "%s gave %s a rating of %d." % (self.user.username,
            self.item.name, self.rating)


class Word(models.Model):
    word = models.CharField(max_length=50)

    def __unicode__(self):
        return self.word


class Tag(models.Model):
    user = models.ForeignKey(User)
    item = models.ForeignKey(Item)
    action = models.ForeignKey(Action, unique=True)

    word = models.ForeignKey(Word)

    def __unicode__(self):
        return "%s tagged %s %s." % (self.user.username,
            self.item.name, self.word.word)


class SimilarityManager(models.Manager):
    def update_user(self, user):
        '''
        Update similarity values for a user against all other users.
        '''
        for user2 in User.objects.all():
            self.update_user_pair(user, user2)

    def update_user_delta(self, user, delta):
        '''
        Update similarity values for a user against all other users after
         an opinion set update, represented by a delta dict.
        '''

        items = list(delta.iterkeys())
        users = Opinion.objects.filter(item__in=items).values_list('user',
            flat=True)

        for user2_id in users:
            user2 = User.objects.get(pk=user2_id)
            self.update_user_pair(user, user2)

    def update_user_pair(self, user1, user2):
        '''
        Update similarity values for a pair of users.
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
    user1 = models.ForeignKey(User)
    user2 = models.ForeignKey(User, related_name="similarity_set2")
    value = models.IntegerField()

    objects = SimilarityManager()

    def __unicode__(self):
        return "S(%s, %s) = %d" % (self.user1.username,
            self.user2.username, self.value)
