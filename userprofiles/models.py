from django.db import models
from django.contrib.auth.models import User
from main.models import Opinion, Similarity

# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    display_name = models.CharField(max_length=64)
    
    def similar(self):
        '''
        Fetches users most similar to self.user, ordered by descending similarity.

        Implementation note: this *might* be a better fit in a User subclass.
        '''
        similar_users = Similarity.objects.filter(user1__exact=self.user).exclude(user2__exact=self.user).order_by('-value')
        return similar_users
