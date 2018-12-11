from django import forms
from novel.models import *


class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SourceForm, self).__init__(*args, **kwargs)
        status_choices = [(0, '正常'), (1, '不可用')]
        self.fields['status'] = forms.ChoiceField(choices=status_choices)


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        status_choices = [(0, '正常'), (1, '隐藏')]
        self.fields['status'] = forms.ChoiceField(choices=status_choices)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        status_choices = [(0, '正常'), (1, '隐藏')]
        self.fields['status'] = forms.ChoiceField(choices=status_choices)


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        status_choices = [(0, '正常'), (1, '下架')]
        self.fields['status'] = forms.ChoiceField(choices=status_choices)


class SourceLinkForm(forms.ModelForm):
    class Meta:
        model = SourceLink
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SourceLinkForm, self).__init__(*args, **kwargs)
        self.fields['book_id'] = forms.ChoiceField(choices=get_book_choices(), label='Book')
        self.fields['source_id'] = forms.ChoiceField(choices=get_source_choices(), label='Source')


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = '__all__'


def get_book_choices():
    res = []
    books = Book.objects.all()
    if len(books) == 0:
        return res
    for book in books:
        res.append((book.id, book.name))
    return res


def get_source_choices():
    res = []
    sources = Source.objects.all()
    if len(sources) == 0:
        return res
    for source in sources:
        res.append((source.id, source.name))
    return res
