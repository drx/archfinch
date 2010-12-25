from celery.decorators import task
from archfinch.main.models import Item

@task
def recommend(category, users):
    recommendations = list(Item.objects.recommended(users[0], category=category))
    return recommendations
