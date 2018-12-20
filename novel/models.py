from django.db import models
from xpinyin import Pinyin


class Source(models.Model):
    name = models.CharField(max_length=30)
    pinyin = models.CharField(max_length=150, default='', blank=True)
    website = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pinyin is None or len(self.pinyin) == 0:
            p = Pinyin()
            self.pinyin = p.get_pinyin(self.name, '')
        super(Source, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=20)
    pinyin = models.CharField(max_length=50, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pinyin is None or len(self.pinyin) == 0:
            p = Pinyin()
            self.pinyin = p.get_pinyin(self.name, '')
        super(Author, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=10)
    pinyin = models.CharField(max_length=50, default='', blank=True)
    status = models.IntegerField()
    parent_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pinyin is None or len(self.pinyin) == 0:
            p = Pinyin()
            self.pinyin = p.get_pinyin(self.name, '')
        super(Category, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=30)
    pinyin = models.CharField(max_length=150, default='', blank=True)
    authors = models.ManyToManyField(Author)
    categories = models.ManyToManyField(Category)
    status = models.IntegerField()
    sources = models.ManyToManyField(Source)
    finish = models.BooleanField(default=False)
    default = models.BooleanField(default=False)
    img = models.ImageField(upload_to='images', default='')
    description = models.CharField(max_length=200, default='')
    clicks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pinyin is None or len(self.pinyin) == 0:
            p = Pinyin()
            self.pinyin = p.get_pinyin(self.name, '')
        super(Book, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class SourceLink(models.Model):
    book_id = models.IntegerField()
    source_id = models.IntegerField()
    link = models.CharField(max_length=300)
    status = models.IntegerField(default=0)

    def no_need_grab(self):
        book = Book.objects.filter(id=self.book_id).first()
        return book is None or book.finish


class Chapter(models.Model):
    title = models.CharField(max_length=30)
    source_id = models.IntegerField()
    book_id = models.IntegerField()
    link = models.CharField(max_length=500, default='')
    content_id = models.IntegerField(default=0)
    number = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    class Meta:
        index_together = [('book_id', 'source_id', 'created_at',), ('title', 'book_id', 'source_id',)]

    def __str__(self):
        return self.title

    @staticmethod
    def exists(chapter):
        return Chapter.objects.filter(title=chapter.title, book_id=chapter.book_id,
                                      source_id=chapter.source_id).count() > 0


class Content(models.Model):
    content = models.CharField(max_length=15000)
    created_at = models.DateTimeField(auto_now_add=True)
