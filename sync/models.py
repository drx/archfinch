from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return 'Sync source (%s)' % (self.name,)


class Synced(models.Model):
    link = models.ForeignKey('links.Link')
    source = models.ForeignKey(Source)

    original_id = models.CharField(max_length=200, db_index=True)

    scraped = models.BooleanField(default=False, db_index=True)
    scrape_attempts = models.IntegerField(default=0)

    def __unicode__(self):
        return 'Synced #%s from %s' % (self.original_id, self.source.name)
