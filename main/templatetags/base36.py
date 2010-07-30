from django import template
from django.utils.http import int_to_base36


register = template.Library()


@register.filter
def base36(value):
    "Converts value to base36"
    return int_to_base36(value)
