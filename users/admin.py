from archfinch.users.models import User
from django.contrib import admin
from archfinch.utils.admin import raw_id_fields_admin


admin.site.register(User, raw_id_fields_admin('referred_by'))
