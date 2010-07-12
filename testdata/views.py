from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from main.models import Opinion, Item, Action
import random


def runtest(request):

    Item.objects.all().delete()
    User.objects.filter(pk__gt=1).delete()
    Opinion.objects.all().delete()
    Action.objects.all().delete()

    for i in xrange(10000):
        for j in xrange(5):
            item = Item(category_id=(j + 1),
                name='Cat%d item #%d' % (j + 1, i))
            item.save()

    for i in xrange(100000):
        u = User.objects.create_user('User%d' % i, 'fake@example.com', 'a')

        # in the order of most interesting to the user to least
        cats = [random.gauss(10, 10), random.gauss(2, 5),
            random.gauss(-2, 5), random.gauss(-5, 5), random.gauss(-10, 5)]

        random.shuffle(cats)

        for cat, cat_n in enumerate(cats):
            cat += 1
            cat_n = int(cat_n)
            if cat_n < 0:
                cat_n = 0
            for k in xrange(cat_n):
                action = Action()
                action.save()
                item_id = abs(int(random.gauss(0, 2000)))
                item = Item.objects.get(name='Cat%d item #%d' % (cat, item_id))
                temp = random.gauss(0, 1)
                if temp > 3:
                    rating = 6
                elif temp > 1.5:
                    rating = 5
                elif temp > 0.5:
                    rating = 4
                elif temp > -0.5:
                    rating = 3
                elif temp > -1.5:
                    rating = 2
                else:
                    rating = 1
                opinion = Opinion(user=u, item=item, action=action,
                    rating=rating)
                opinion.save()

    html = "<html><body>It is done.</body></html>" % temp
    return HttpResponse(html)
