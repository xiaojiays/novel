from django.db import models
from novel.util import Util


class Book(models.Model):
    name = models.CharField(max_length=200)
    category_id = models.IntegerField()
    created_at = models.IntegerField()
    updated_at = models.IntegerField()
    uid = models.CharField(max_length=32, default='')
    source = models.CharField(max_length=100, default='')
    sid = models.CharField(max_length=50, default='')
    status = models.IntegerField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.uid is None or len(self.uid) == 0:
            self.uid = Util.md5(self.name + str(self.created_at))
        super(Book, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return self.name


class Chapter(models.Model):
    title = models.CharField(max_length=200)
    source = models.CharField(max_length=200, default='')
    link = models.CharField(max_length=500, default='')
    book_id = models.IntegerField(default=0)
    content_id = models.IntegerField(default=0)
    updated_at = models.IntegerField(default=0)
    created_at = models.IntegerField(default=0)
