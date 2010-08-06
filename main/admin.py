from main.models import Category, Item, ItemProfile, Opinion, Action, Similarity
from django.contrib import admin


class ItemAdmin(admin.ModelAdmin):
    raw_id_fields = ('parent',)


class ItemProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('item',)

admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemProfile, ItemProfileAdmin)
admin.site.register(Opinion)
admin.site.register(Action)
admin.site.register(Similarity)
