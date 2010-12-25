from celery.decorators import task

@task
def recommend(category, users):
    recommendations = list(users[0].recommend(category=category))
    return recommendations
