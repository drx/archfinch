from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Item(models.Model):
    category = models.ForeignKey(Category)
    parent = models.ForeignKey('Item', null=True, blank=True)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Action(models.Model):
    time = models.DateTimeField(auto_now_add=True, unique=False)
    
    def __unicode__(self):
        return self.time.ctime()

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
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True)

    def __unicode__(self):
        return "%s gave %s a rating of %d." % (self.user.username, self.item.name, self.rating)

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
        return "%s tagged %s %s." % (self.user.username, self.item.name, self.word.word)
