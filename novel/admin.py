from django.contrib import admin
from novel.form import *


class SourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'website', 'status_name', 'created_at']
    form = SourceForm

    @staticmethod
    def status_name(obj):
        if obj.status == 0:
            return '正常'
        return '不可用'


class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'author', 'status_name', 'created_at']
    form = BookForm

    @staticmethod
    def category(obj):
        return list(obj.categories.all())

    @staticmethod
    def author(obj):
        return obj.authors.first()

    @staticmethod
    def status_name(obj):
        if obj.status == 0:
            return '正常'
        return '下架'


class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status_name', 'created_at']
    form = AuthorForm

    @staticmethod
    def status_name(obj):
        if obj.status == 0:
            return '正常'
        return '隐藏'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'status_name', 'created_at']
    form = CategoryForm

    @staticmethod
    def status_name(obj):
        if obj.status == 0:
            return '正常'
        return '隐藏'

    @staticmethod
    def parent(obj):
        if obj.parent_id == 0:
            return '-'
        category = Category.objects.filter(id=obj.parent_id).first()
        if category is None:
            return '-'
        return category.name


class SourceLinkAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'source', 'link', 'status_name']
    form = SourceLinkForm

    @staticmethod
    def book(obj):
        return Book.objects.filter(id=obj.book_id).first()

    @staticmethod
    def source(obj):
        return Source.objects.filter(id=obj.source_id).first()

    @staticmethod
    def status_name(obj):
        if obj.status == 0:
            return '未初始'
        return '已初始'


admin.site.register(Source, SourceAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(SourceLink, SourceLinkAdmin)
