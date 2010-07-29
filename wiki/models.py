from django.db import models
from users.models import User


class RevisionText(models.Model):
    text = models.TextField()

    def __unicode__(self):
        return self.text


class Revision(models.Model):
    user = models.ForeignKey(User)
    text = models.ForeignKey(RevisionText)


class Page(models.Model):
    current = models.ForeignKey(Revision)

    def render(self):
        return self.current.text
