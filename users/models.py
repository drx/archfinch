from django.db import models
from django.contrib.auth.models import User as BaseUser, UserManager as BaseUserManager
from main.models import Opinion, Similarity

class User(BaseUser):
    objects = BaseUserManager()

    def similar(self):
        '''
        Fetches users most similar to self.user, ordered by descending similarity.
        '''
        similar_users = Similarity.objects.filter(user1__exact=self).exclude(user2__exact=self).order_by('-value')
        return similar_users

    
