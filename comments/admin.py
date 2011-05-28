from archfinch.comments.models import Comment
from django.contrib import admin
from archfinch.utils.admin import raw_id_fields_admin


admin.site.register(Comment, raw_id_fields_admin('parent', 'submitter'))
