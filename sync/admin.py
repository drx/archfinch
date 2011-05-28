from archfinch.sync.models import Source, Synced
from django.contrib import admin
from archfinch.utils.admin import raw_id_fields_admin


admin.site.register(Source)
admin.site.register(Synced, raw_id_fields_admin('link'))
