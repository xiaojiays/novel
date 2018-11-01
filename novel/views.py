from django.shortcuts import render_to_response

from novel.models import Book
from novel.util import Util
from novel import settings


def home(request):
    return render_to_response('home.html')


def book_list(request, *args, **kwargs):
    page = Util.get_page(kwargs)
    size = 50
    offset = (page - 1) * size
    books = Book.objects.filter(status=0).all()[offset:size]
    return render_to_response('book_list.html', {'books': books, 'settings': settings})


def book(request, *args, **kwargs):
    uid = kwargs.get('uid')
    if uid is None:
        print(1)

    b = Book.objects.filter(uid=str(uid)).first()
    if b is None:
        print(1)

    return render_to_response('book.html')


def register(request):
    return render_to_response('register.html')


def login(request):
    return render_to_response('login.html')
