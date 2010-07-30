from django import forms
from django.db import models
from users.models import User


class Page(models.Model):
    def render(self):
        return self.current().text.render()

    def current(self):
        return self.revisions.latest()

    def __unicode__(self):
        return 'Page #{id}'.format(id=self.pk)


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
        return 'Revision {time} of {page}'.format(time=self.time, page=self.page)

    class Meta:
        get_latest_by = 'time'


class PageForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 100, 'rows': 20, 'class': 'resizable'})
    )

    class Media:
        js = ('js/textarea.js',)
