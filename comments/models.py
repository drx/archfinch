from django.db import models
from django.forms import ModelForm
from archfinch.main.models import Item


class Comment(Item):
    text = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        if len(self.text) > 32:
            return "%s..." % (self.text[:32])
        else:
            return self.text

    post_save_verb = 'commented:'


class AddCommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('tags',)
