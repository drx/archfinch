import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'archfinch.settings'

from titlecase import titlecase
from archfinch.main.models import Item

a = 0
b = []
while True:
    for i in Item.objects.filter(category=7).order_by('id')[a:a+1000]:
        t = titlecase(i.name)
        if i.name != t:
            i.name = t
            b.append(i)
        a = a+1
    for c in b:
        c.save()
    b = []
