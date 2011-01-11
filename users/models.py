from django.db import models
from django.db.models import F
from django.contrib.auth.models import User as BaseUser, UserManager as BaseUserManager
from django.utils.http import int_to_base36
from django.core.urlresolvers import reverse
from archfinch.main.models import Opinion, Similarity, Item


class User(BaseUser):
    objects = BaseUserManager()

    karma = models.IntegerField(default=0)

    def self_lists(self):
        lists = [
            {'name': 'ignored', 'id': '!ignored'},
            {'name': 'queue', 'id': '!queue'},
        ]
        for list in self.list_set.exclude(ignored=True).exclude(queue=True):
            lists.append({'name': list.name, 'id': int_to_base36(list.id)})

        return lists
    

    def categories(self, opinions=None):
        '''
        Fetches categories the user has rated in.
        '''
        if opinions is None:
            opinions = Opinion.objects.filter(user=self).select_related('item__category')
        categories = opinions.values_list('item__category__id', 'item__category__element_plural', 'item__category__slug')
        categories = set(categories)

        return categories


    def similar(self):
        '''
        Fetches users most similar to self.user, ordered by descending
         similarity.
        '''
        similar_users = Similarity.objects.filter(user1__exact=self).exclude(
            user2__exact=self).filter(value__gt=0).order_by('-value', 'user2')
        return similar_users


    def add_points(self, n):
        self.karma = F('karma') + n
        self.save()


    def karma_place(self):
        return User.objects.filter(karma__gt=self.karma).count()+1
