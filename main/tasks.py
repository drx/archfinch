from datetime import timedelta
from django.db.models.signals import post_save
from celery.decorators import task, periodic_task
from staticgenerator import recursive_delete
from archfinch.main.models import Item, Opinion, Action, Similarity
from archfinch.links.models import Link
from archfinch.comments.models import Comment

@task
def recommend(category, fresh, tags, users):
    if category is not None and category.id in (9,10,11) or fresh:
        # links
        recommendations = list(Link.objects.recommended(users[0], category=category, tags=tags))
    else:
        recommendations = list(Item.objects.recommended(users, category=category))
    return recommendations


@task
def recommend_generic(category, fresh, tags):
    if category is not None and category.id in (9,10,11) or fresh:
        # links
        return list(Link.objects.recommended_generic(category=category, tags=tags))
    else:
        return list(Item.objects.recommended_generic(category=category))


@task
def opinion_set(user, item, rating):
    opinion, created = Opinion.objects.get_or_create(user=user, item=item,
        defaults={'rating': rating})
    old_rating = opinion.rating
    opinion.rating = rating
    opinion.save()

    action, created = Action.objects.get_or_create(type=Action.types['rating'], opinion=opinion, user=user)
    action.save()

    if created or rating != old_rating:
        delta = {item.id: ('set', old_rating, rating)}
        Similarity.objects.update_item_delta(user, delta)
        user.add_points(1)

@task
def opinion_remove(user, item):
    opinion = Opinion.objects.get(user=user, item=item)
    old_rating = opinion.rating
    opinion.delete()

    delta = {item.id: ('remove', old_rating)}
    Similarity.objects.update_item_delta(user, delta)
    user.add_points(-1)


@periodic_task(run_every=timedelta(hours=1))
def static_delete():
    recursive_delete('/item')


@periodic_task(run_every=timedelta(minutes=1))
def static_republish():
    from archfinch.utils.cache import republish_static
    republish_static()
