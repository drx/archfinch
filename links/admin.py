from archfinch.links.models import Link
from django.contrib import admin
from archfinch.utils.admin import raw_id_fields_admin


admin.site.register(Link, raw_id_fields_admin('parent', 'submitter'))
