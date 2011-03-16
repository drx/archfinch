from django.db import models
from archfinch.main.models import Item

class LinkManager(models.Manager):
    def recommended(self, user, category=None, category_id=None):
        '''
        Fetches links recommended for the user.
        '''

        where = ''
        params = [user.id]*2
        if category is not None and category:
            category_id = category.id

        if category_id is not None:
            where += ' AND mi.category_id = %s'
            params.append(category_id)

        # Select items in order of their recommendation to self
        # 
        # recommendation =
        #    sum (rating-3)*similarity for all similar users
        # 
        #    where 
        #      rating: what the user has rated the item
        #      similarity: similarity between the user and self
        recommended = Link.objects.raw("""
            SELECT * FROM (SELECT mi.id, mi.category_id, mi.parent_id, mi.name, ll.item_ptr_id, ll.time,

             SUM((mo.rating-3)*ms.value)/
             (CASE
               WHEN extract(epoch from now()-ll.time)/86400 < 1
               THEN 1
               ELSE 86400/extract(epoch from now()-ll.time)
              END
             ) AS recommendation,

             mc.element_singular AS category_element,
             COALESCE((SELECT rating FROM main_opinion mo WHERE mo.user_id=%s AND mo.item_id=mi.id)) as rating
            FROM main_similarity ms
             INNER JOIN main_opinion mo
              ON ms.user2_id=mo.user_id
             INNER JOIN main_item mi
              ON mo.item_id=mi.id
             INNER JOIN main_category mc
              ON mc.id=mi.category_id
             INNER JOIN links_link ll
              ON ll.item_ptr_id=mi.id
            WHERE ms.user1_id = %s
             AND ms.value > 0
             """+where+"""
            GROUP BY mi.id, mi.category_id, mi.parent_id, mi.name, category_element, ll.item_ptr_id, ll.time
            ORDER BY recommendation DESC) AS recommended WHERE recommendation > 0""",
            params)

        return recommended


class Link(Item):
    url = models.URLField(verify_exists=False, max_length=1000, blank=True, null=True)
    time = models.DateTimeField(auto_now=True, unique=False)

    objects = LinkManager()
