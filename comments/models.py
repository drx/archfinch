from django.db import models
from django.db.models.signals import post_save
from archfinch.main.models import Item
from archfinch.utils.spam import AntiSpamModelForm


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


class AddCommentForm(AntiSpamModelForm):
    class Meta:
        model = Comment
        exclude = ('tags',)

def comment_count_update(sender, **kwargs):
    instance = kwargs['instance']

    instance.root().update_comment_count()

post_save.connect(comment_count_update, Comment)

