from archfinch.main.models import Category, Item, ItemProfile, Opinion, Action, Similarity, ItemOption, ItemStats, Tag, TagBlock, TagFollow, Tagged, Review
from django.contrib import admin
from archfinch.utils.admin import raw_id_fields_admin


admin.site.register(Category)
admin.site.register(Item, raw_id_fields_admin('parent', 'submitter'))
admin.site.register(ItemProfile, raw_id_fields_admin('item'))
admin.site.register(ItemOption, raw_id_fields_admin('item'))
admin.site.register(ItemStats, raw_id_fields_admin('item'))
admin.site.register(Opinion)
admin.site.register(Action)
admin.site.register(Similarity)
admin.site.register(Review, raw_id_fields_admin('user', 'item'))
admin.site.register(Tag)
admin.site.register(TagBlock, raw_id_fields_admin('user'))
admin.site.register(TagFollow, raw_id_fields_admin('user'))
admin.site.register(Tagged, raw_id_fields_admin('item', 'user'))
