from django.db import models
from novel.util import Util


class Source(models.Model):
    name = models.CharField(max_length=30)
    website = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=10)
    status = models.IntegerField()
    parent_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=30)
    authors = models.ManyToManyField(Author)
    categories = models.ManyToManyField(Category)
    uid = models.CharField(max_length=32, default='', blank=True)
    status = models.IntegerField()
    sources = models.ManyToManyField(Source)
    finish = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.uid is None or len(self.uid) == 0:
            self.uid = Util.md5(self.name + str(self.created_at))
        super(Book, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class SourceLink(models.Model):
    book_id = models.IntegerField()
    source_id = models.IntegerField()
    link = models.CharField(max_length=300)
    status = models.IntegerField(default=0)


class Chapter(models.Model):
    title = models.CharField(max_length=30)
    source_id = models.IntegerField()
    book_id = models.IntegerField()
    link = models.CharField(max_length=500, default='')
    content_id = models.IntegerField(default=0)
    uid = models.CharField(max_length=32, default='')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.uid is None or len(self.uid) == 0:
            self.uid = Util.md5(self.title + str(self.created_at))
        super(Chapter, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.title

    @staticmethod
    def exists(chapter):
        return Chapter.objects.filter(source_id=chapter.source_id).filter(book_id=chapter.book_id).filter(
            title=chapter.title).count() > 0


class Content(models.Model):
    content = models.CharField(max_length=15000)
    created_at = models.DateTimeField(auto_now_add=True)
