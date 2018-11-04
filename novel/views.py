from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator

from novel.models import Book, Chapter, Source
from novel.util import Util
from novel import settings

import math


def home(request, *args, **kwargs):
    size = 50
    book_list = Book.objects.all()
    paginator = Paginator(book_list, size)
    page = Util.get_page(kwargs)
    books = paginator.page(page)
    total = book_list.count()
    total_page = math.ceil(total / size)
    pages = get_pages(page, total_page)

    data = []
    for b in books:
        data.append(get_data(b))

    params = {
        'request': request,
        'settings': settings,
        'home_page': True,
        'books': books,
        'total': total,
        'total_page': total_page,
        'data': data,
        'pages': pages,
        'page': page,

    }
    return render_to_response('home.html', params)


def get_data(b):
    category = b.categories.first()
    author = b.authors.first()
    chapter = Chapter.objects.filter(book_id=b.id).order_by('-id').first()

    item = {
        'pinyin': b.pinyin,
        'name': b.name,
        'img': b.img,
        'finish': b.finish,
        'desc': b.description,
    }
    if category is not None:
        item.setdefault('category', category)
    if author is not None:
        item.setdefault('author', author)
    if chapter is not None:
        item.setdefault('chapter', chapter)
    return item


def get_pages(page, total_page):
    start_page = get_start_page(page, total_page)
    end_page = start_page + 8
    if end_page > total_page:
        end_page = total_page

    pages = []
    while start_page <= end_page:
        pages.append(start_page)
        start_page += 1
    return pages


def get_start_page(page, total_page):
    if total_page <= 9:
        return 1
    if page <= 5:
        return 1
    if total_page - page >= 4:
        return page - 4
    return page - (8 - (total_page - page))


def book(request, *args, **kwargs):
    pinyin = kwargs.get('pinyin')
    if pinyin is None:
        return page_not_found(request)

    b = Book.objects.filter(pinyin=str(pinyin)).first()
    if b is None:
        return page_not_found(request)

    data = get_data(b)
    chapters = get_chapters(b)
    params = {
        'data': data,
        'settings': settings,
        'chapters': chapters,
    }

    return render_to_response('book.html', params)


def get_chapters(b):
    chapters = Chapter.objects.filter(book_id=b.id).order_by('-id').all()[:20]
    if len(chapters) == 0:
        return []

    res = []
    sources = {}
    for chapter in chapters:
        source = sources.get(chapter.source_id)
        if source is None:
            source = Source.objects.filter(id=chapter.source_id).first()
            sources.setdefault(chapter.source_id, source)
        item = {
            'id': chapter.id,
            'title': chapter.title,
            'link': chapter.link,
            'updated_at': chapter.updated_at,
            'source_name': source.name,
            'source_pinyin': source.pinyin,
        }
        res.append(item)
    return res


def jump(request):
    link = request.GET.get('link')
    return render_to_response('jump.html', {'link': link})


def sbc(request, *args, **kwargs):
    source = Source.objects.filter(pinyin=kwargs.get('s')).first()
    if source is None:
        return page_not_found(request)

    b = Book.objects.filter(pinyin=kwargs.get('b')).first()
    if b is None:
        return page_not_found(request)

    chapters = Chapter.objects.filter(source_id=source.id).filter(book_id=b.id).order_by('-id').all()
    params = {
        'source': source,
        'book': b,
        'chapters': chapters,
    }
    return render_to_response('sbc.html', params)


def chapter_list(request, *args, **kwargs):
    b = Book.objects.filter(pinyin=kwargs.get('pinyin')).first()
    if b is None:
        return page_not_found(request)

    return render_to_response('chapters.html')


def page_not_found(request):
    return home(request)


def server_error(request):
    return home(request)
