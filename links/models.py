from django.db import models
from archfinch.main.models import Item

class Link(Item):
    url = models.URLField(verify_exists=False, max_length=1000, blank=True, null=True)
