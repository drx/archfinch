from django.contrib import admin

def raw_id_fields_admin(*args):
    fields = args
    class cls(admin.ModelAdmin):
        raw_id_fields = fields

    return cls


