from django.shortcuts import render_to_response
from django.core.paginator import Paginator
from django.db.models import Count
from novel import settings
from novel.models import Book, Category, Chapter, Source
from novel.util import Util
from novel import views

import math


def home(request, *args, **kwargs):
    book_list = Book.objects.filter(status=0).all()
    return render(request, book_list, '所有小说', '', kwargs)


def hot(request, *args, **kwargs):
    book_list = Book.objects.filter(status=0).order_by('-clicks').all()
    return render(request, book_list, '热门小说', '/hot', kwargs)


def category(request):
    categories = Category.objects.filter(status=0).all()
    params = {
        'categories': categories,
        'title': '小说分类',
        'settings': settings,
    }
    return render_to_response('m/category.html', params)


def category_list(request, *args, **kwargs):
    category = Category.objects.filter(pinyin=kwargs.get('pinyin')).first()
    if category is None:
        return views.page_not_found(request)

    book_list = Book.objects.filter(categories=category).order_by('-clicks').all()
    return render(request, book_list, category.name + '小说', '/category/' + category.pinyin, kwargs)


def finish(request, *args, **kwargs):
    book_list = Book.objects.filter(finish=1).order_by('-clicks').all()
    return render(request, book_list, '全本小说', '/finish', kwargs)


def search(request):
    books = Book.objects.filter(status=0).order_by('-clicks').all()[:10]
    params = {
        'title': '搜书',
        'books': books,
        'settings': settings,
    }
    return render_to_response('m/search.html', params)


def render(request, book_list, title, prefix, kwargs):
    size = 30
    paginator = Paginator(book_list, size)
    page = Util.get_page(kwargs)
    books = paginator.page(page)
    total = book_list.count()
    total_page = math.ceil(total / size)
    pages = views.get_pages(page, total_page)
    params = {
        'request': request,
        'settings': settings,
        'home_page': True,
        'books': books,
        'total': total,
        'total_page': total_page,
        'data': views.get_datas(books),
        'pages': pages,
        'page': page,
        'title': title,
        'prefix': prefix,

    }
    return render_to_response('m/home.html', params)


def book(request, pinyin):
    book = Book.objects.filter(status=0).filter(pinyin=pinyin).first()
    if book is None:
        return views.page_not_found(request)

    source_id = get_source_id(book.id)

    chapters = views.get_chapters(book)
    data = views.get_data(book)
    params = {
        'book': data,
        'settings': settings,
        'chapters': chapters,
        'hottest': views.hottest_books(6),
        'archives': views.archives(data.get('author')),
        'sources': views.get_sources(book),
        'source_id': source_id,
    }
    return render_to_response('m/book.html', params)


def get_book_chapters(b, source_id):
    chapters = Chapter.objects.filter(book_id=b.id, source_id=source_id).order_by('-id').all()[:20]
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
            'source_id': source_id,
        }
        res.append(item)
    return res


def get_source_id(book_id):
    source = Chapter.objects.annotate(total=Count('id')).filter(book_id=book_id).values('source_id').order_by(
        '-total').first()
    return source['source_id']


def chapters(request, *args, **kwargs):
    page = Util.get_page(kwargs)
    book = Book.objects.filter(status=0).filter(pinyin=kwargs.get('pinyin')).first()
    if book is None:
        return views.page_not_found(request)

    source_id = request.GET.get('sid')
    if source_id is None:
        source_id = get_source_id(book.id)

    size = 50
    offset = (page - 1) * size
    chapters = Chapter.objects.filter(book_id=book.id, source_id=source_id)
    total = chapters.count()

    if request.GET.get('sort') is not None and request.GET.get('sort') == 'desc':
        chapters = chapters.order_by('-number')
    chapters = chapters.all()[offset:offset + size]
    total_page = math.ceil(total / size)
    cp = chapter_pages(total, size)
    params = {
        'book': book,
        'total': total,
        'chapters': chapters,
        'settings': settings,
        'pages': views.get_pages(page, total_page),
        'chapter_pages': cp,
        'page': page,
        'total_page': total_page,
        "target": cp[page - 1],
        'sort': request.GET.get('sort'),
        'start': offset,
        'sources': get_book_sources(book, source_id),
    }
    return render_to_response('m/chapters.html', params)


def chapter_pages(total, size):
    res = []
    i = 1
    while i < total:
        res.append(str(i) + '-' + str(i + size - 1) + '章')
        i += 50
    return res


def get_book_sources(book, source_id):
    sources = book.sources.all()
    if sources is None:
        return sources

    res = []
    for source in sources:
        if source_id is not None and int(source.id) == int(source_id):
            res.insert(0, source)
        else:
            res.append(source)
    return res


def search_list(request, *args, **kwargs):
    keyword = request.GET.get('key')
    books = Book.objects.filter(status=0).filter(name__icontains=keyword).all()
    return render(request, books, keyword + '搜索结果', '/search', kwargs)
