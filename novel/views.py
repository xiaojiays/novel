from django.shortcuts import render_to_response

from novel.models import Book
from novel.util import Util
from novel import settings


def book_list(request, *args, **kwargs):
    page = Util.get_page(kwargs)
    size = 50
    offset = (page - 1) * size
    books = Book.objects.filter(status=0).all()[offset:size]
    return render_to_response('book_list.html', {'books': books, 'settings': settings})
