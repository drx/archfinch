from django.db import models
from django.contrib.auth.models import User as BaseUser, UserManager as BaseUserManager
from main.models import Opinion, Similarity, Item

class User(BaseUser):
    objects = BaseUserManager()

    def similar(self):
        '''
        Fetches users most similar to self.user, ordered by descending similarity.
        '''
        similar_users = Similarity.objects.filter(user1__exact=self).exclude(user2__exact=self).order_by('-value')
        return similar_users

    def recommend(self):
        '''
        Fetches items recommended for the user.

        The algorithms needs work.
        '''

        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT mi.id, mi.category_id, mi.parent_id, mi.name,
             SUM(mo.rating-3) AS rating_sum
            FROM main_similarity ms
             INNER JOIN main_opinion mo
              ON ms.user2_id=mo.user_id
             INNER JOIN main_item mi
              ON mo.item_id=mi.id
            WHERE ms.user1_id=%s
             AND ms.user2_id!=%s
             AND ms.value > 0
            GROUP BY mi.id, mi.category_id, mi.parent_id, mi.name
            ORDER BY rating_sum DESC""",
            [self.id, self.id])
        result_list = []
        for row in cursor.fetchall():
            if row[4] <= 0:
                break
            p = Item(id=row[0], category_id=row[1], parent_id=row[2], name=row[3])
            p.rating_sum = row[4]
            result_list.append(p)
        return result_list

 
