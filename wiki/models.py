from django import forms
from django.db import models
from archfinch.users.models import User
from archfinch.utils.spam import AntiSpamForm


class Page(models.Model):
    def render(self):
        return self.current().text.render()

    def current(self):
        return self.revisions.latest()

    def __unicode__(self):
        try:
            return 'Page #{id}'.format(id=self.pk)
        except AttributeError:
            # python 2.5 compatibility 
            return 'Page #%s' % (self.pk)


class RevisionText(models.Model):
    text = models.TextField()

    def render(self):
        return self.text

    def __unicode__(self):
        words = self.text.split()
        if len(words) > 10:
            return ' '.join(words[:10]) + '...'
        else:
            return ' '.join(words)


class Revision(models.Model):
    page = models.ForeignKey(Page, related_name='revisions')
    user = models.ForeignKey(User)
    text = models.OneToOneField(RevisionText)
    time = models.DateTimeField(auto_now_add=True, unique=False)

    def __unicode__(self):
        try:
            return 'Revision {time} of {page}'.format(time=self.time, page=self.page)
        except AttributeError:
            # python 2.5 compatibility 
            return 'Revision %s of %s' % (self.time, self.page)

    class Meta:
        get_latest_by = 'time'


class PageForm(AntiSpamForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 20, 'class': 'resizable'})
    )
