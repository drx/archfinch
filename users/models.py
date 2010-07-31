from django.db import models
from django.contrib.auth.models import (User as BaseUser,
    UserManager as BaseUserManager)
from main.models import Opinion, Similarity, Item


class User(BaseUser):
    objects = BaseUserManager()

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
            user2__exact=self).filter(value__gt=0).order_by('-value')
        return similar_users


    def recommendation(self, item):
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
            [self.id, self.id, item.id])

        items = list(items)
        if items:
            return items[0].recommendation
        else:
            return 0


    def recommend(self, category=None):
        '''
        Fetches items recommended for the user (which the user has not already rated)
         and returns an iterator.

        The algorithm should cut off at a certain amount of similar users,
         as potentially it's millions of similar users.
        '''
        from itertools import takewhile

        where = ''
        params = [self.id, self.id, self.id]
        if category is not None and category:
            where += ' AND mi.category_id = %s'
            params.append(category.id)

        # Select items in order of their recommendation to self
        # 
        # recommendation =
        #    sum (rating-3)*similarity for all similar users
        # 
        #    where 
        #      rating: what the user has rated the item
        #      similarity: similarity between the user and self
        recommended = Item.objects.raw("""
            SELECT mi.id, mi.category_id, mi.parent_id, mi.name,
             SUM((mo.rating-3)*ms.value) AS recommendation
            FROM main_similarity ms
             INNER JOIN main_opinion mo
              ON ms.user2_id=mo.user_id
             INNER JOIN main_item mi
              ON mo.item_id=mi.id
            WHERE ms.user1_id=%s
             AND ms.user2_id!=%s
             AND ms.value > 0
             AND NOT EXISTS
              (SELECT 1 FROM main_opinion mo2
               WHERE mo2.item_id=mi.id AND mo2.user_id=%s)
             """+where+"""
            GROUP BY mi.id, mi.category_id, mi.parent_id, mi.name
            ORDER BY recommendation DESC""",
            params)

        # have to do it this way -- RawQuerySet doesn't have filter, etc.
        recommended = takewhile(lambda x: x.recommendation > 0, recommended)

        return recommended
