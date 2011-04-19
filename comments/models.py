from django.db import models
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

    def comment_tree(self):
        def traverse(comment):
            flat = []
            flat.append({'type': 'comment', 'comment': comment})
            for child in comment.children.all():
                flat.append({'type': 'in'})
                flat.extend(traverse(child))
                flat.append({'type': 'out'})
            return flat

        return traverse(self)
