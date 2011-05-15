from django.db import models
from archfinch.main.models import Item
from archfinch.users.models import User

class LinkManager(models.Manager):
    def recommended_generic(self, category=None, tags=None):
        '''
        Fetches links recommended generally (not for a specific user).
        '''

        where = ''
        params = {}

        if category is not None:
            where += 'WHERE mi.category_id = %(category_id)s'
            params['category_id'] = category.id

        if tags:
            for tag in tags:
                where += ' AND EXISTS (SELECT 1 FROM main_tagged mtgd WHERE mi.id = mtgd.item_id AND mtgd.tag_id = %d)' % (int(tag.id))

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

             SUM((mo.rating-3)) *
               (86400/extract(epoch from now()-ll.time))^2
             AS recommendation,

             mc.element_singular AS category_element
            FROM main_opinion mo
              
             INNER JOIN main_item mi
              ON mo.item_id=mi.id
             INNER JOIN main_category mc
              ON mc.id=mi.category_id
             INNER JOIN links_link ll
              ON ll.item_ptr_id=mi.id
             
             """+where+"""
            GROUP BY mi.id, mi.category_id, mi.parent_id, mi.name, category_element, ll.item_ptr_id, ll.time
            ORDER BY date_trunc('day', ll.time) DESC, recommendation DESC) AS recommended WHERE recommendation > 0""",
            params)

        return recommended


    def recommended(self, user, category=None, category_id=None, tags=None):
        '''
        Fetches links recommended for the user.
        '''

        where = ''
        joins = ''
        params = {'user_id': user.id}
        if category is not None and category:
            category_id = category.id

        if category_id is not None:
            where += ' AND mi.category_id = %(category_id)s'
            params['category_id'] = category_id

        if tags:
            for tag in tags:
                where += ' AND EXISTS (SELECT 1 FROM main_tagged mtgd WHERE mi.id = mtgd.item_id AND mtgd.tag_id = %d)' % (int(tag.id))

            archfinch_user = User.objects.get(username='archfinch')
            ms_union = 'UNION SELECT %d, %d, 1' % (user.id, archfinch_user.id)

        else:
            ms_union = ''

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

             SUM((mo.rating-3)*ms.value) *
               (86400/extract(epoch from now()-ll.time))^2
             AS recommendation,
             COALESCE((SELECT rating FROM main_opinion mo WHERE mo.user_id=%(user_id)s AND mo.item_id=mi.id)) AS rating,

             mc.element_singular AS category_element
            FROM (SELECT user1_id, user2_id, value FROM main_similarity ms """+ms_union+""") as ms
             INNER JOIN main_opinion mo
              ON ms.user2_id=mo.user_id
             INNER JOIN main_item mi
              ON mo.item_id=mi.id
             INNER JOIN main_category mc
              ON mc.id=mi.category_id
             INNER JOIN links_link ll
              ON ll.item_ptr_id=mi.id
            WHERE ms.user1_id = %(user_id)s
             AND ms.value > 0
             AND NOT EXISTS (SELECT 1 FROM main_tagblock mtb, main_tagged mtgd WHERE mtgd.tag_id=mtb.tag_id AND mtb.user_id=%(user_id)s AND mtgd.item_id=ll.item_ptr_id)
             """+where+"""
            GROUP BY mi.id, mi.category_id, mi.parent_id, mi.name, category_element, ll.item_ptr_id, ll.time
            ORDER BY date_trunc('day', ll.time) DESC,recommendation DESC) AS recommended WHERE recommendation > 0""",
            params)

        return recommended


class ImageURLField(models.CharField):
    """Image URL field, stored as url,width,height in the database"""
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None: return
        if not isinstance(value, basestring): return value
        fields = value.split(',')
        if len(fields) < 3:
            return {'url': fields[0]}
        return {'url': fields[0], 'width': int(fields[1]), 'height': int(fields[2])}

    def get_prep_value(self, value):
        if value is None: return
        try:
            return ','.join([value['url'], str(value['width']), str(value['height'])])
        except KeyError:
            return value['url']


class Link(Item):
    url = models.URLField(verify_exists=False, max_length=1000, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True, unique=False)

    thumbnail = ImageURLField(max_length=1000, blank=True, null=True)
    image = ImageURLField(max_length=1000, blank=True, null=True)

    html = models.TextField(max_length=1000, blank=True, null=True)    

    objects = LinkManager()

    def age(self):
        import datetime
        age = (datetime.datetime.now() - self.time)
        return age.seconds+age.days*60*60*24

    def views(self):
        age = self.age()
        multiplier = 113 + self.id % 20
        if age < 15*60:
            views = (age/900.)**2 * multiplier
        elif age < 60*60*24:
            views = (age/900.) * multiplier
        else:
            views = 96 * multiplier + age/360.

        return int(views)
