from django.shortcuts import render_to_response
from django.core.paginator import Paginator

from novel.models import Book, Chapter, Source, Author, Category
from novel.util import Util
from novel import settings

import math


def home(request, *args, **kwargs):
    size = 50
    book_list = Book.objects.filter(status=0).all()
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
        'book': get_default_book(),
        'hottest': hottest_books(),
        'newest': newest_books(),

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
    end_page = start_page + 6
    if end_page > total_page:
        end_page = total_page

    pages = []
    while start_page <= end_page:
        pages.append(start_page)
        start_page += 1
    return pages


def get_start_page(page, total_page):
    if total_page <= 7:
        return 1
    if page <= 4:
        return 1
    if total_page - page >= 3:
        return page - 3
    return page - (6 - (total_page - page))


def get_default_book():
    return Book.objects.filter(default=1).filter(status=0).order_by('-id').first()


def book(request, *args, **kwargs):
    pinyin = kwargs.get('pinyin')
    if pinyin is None:
        return page_not_found(request)

    b = Book.objects.filter(pinyin=str(pinyin)).filter(status=0).first()
    if b is None:
        return page_not_found(request)

    data = get_data(b)
    chapters = get_chapters(b)
    params = {
        'book': data,
        'settings': settings,
        'chapters': chapters,
        'book_page': True,
        'hottest': hottest_books(7),
        'archives': archives(data.get('author')),
        'sources': get_sources(b),
    }

    return render_to_response('book.html', params)


def get_chapters(b):
    chapters = Chapter.objects.filter(book_id=b.id).order_by('-number').all()[:20]
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
            'source_id': source.id,
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

    b = Book.objects.filter(pinyin=kwargs.get('b')).filter(status=0).first()
    if b is None:
        return page_not_found(request)

    chapters = Chapter.objects.filter(source_id=source.id).filter(book_id=b.id).order_by('-number').all()
    params = {
        'source': source,
        'book': b,
        'chapters': chapters,
        'book_page': True,
        'settings': settings,
    }
    return render_to_response('sbc.html', params)


def chapter_list(request, *args, **kwargs):
    b = Book.objects.filter(pinyin=kwargs.get('pinyin')).first()
    if b is None:
        return page_not_found(request)

    category = b.categories.first()

    size = 50
    chapters = Chapter.objects.filter(book_id=b.id).order_by('-number').all()
    total = chapters.count()
    paginator = Paginator(chapters, size)
    page = Util.get_page(kwargs)
    chapters = paginator.page(page)
    total_page = math.ceil(total / size)
    pages = get_pages(page, total_page)

    params = {
        'book': b,
        'category': category,
        'chapters': format_chapters(chapters),
        'page': page,
        'pages': pages,
        'total_page': total_page,
        'total': total,
        'book_page': True,
        'settings': settings,
        'newest': newest_books(),
        'hottest': hottest_books(),
    }

    return render_to_response('chapters.html', params)


def format_chapters(chapters):
    if len(chapters) == 0:
        return chapters

    source_ids = []
    for chapter in chapters:
        source_ids.append(chapter.source_id)
    sources = Source.objects.filter(id__in=source_ids).all()
    if len(sources) == 0:
        return chapters

    source_map = {}
    for source in sources:
        source_map.setdefault(source.id, source)

    res = []
    for chapter in chapters:
        item = {
            'title': chapter.title,
            'id': chapter.id,
            'link': chapter.link,
            'updated_at': chapter.updated_at
        }
        source = source_map.get(chapter.source_id)
        if source is not None:
            item.setdefault('source_name', source.name)
            item.setdefault('source_pinyin', source.pinyin)
        res.append(item)
    return res


def newest(request, *args, **kwargs):
    page = Util.get_page(kwargs)
    books = Book.objects.filter(status=0).all()
    params = show_list(books, page)
    params.setdefault('newest_page', True)
    return render_to_response('newest.html', params)


def finish(request, *args, **kwargs):
    page = Util.get_page(kwargs)
    books = Book.objects.filter(status=0).filter(finish=1).all()
    params = show_list(books, page)
    params.setdefault('finish_page', True)
    return render_to_response('finish.html', params)


def show_list(books, page):
    size = 50
    total = books.count()
    paginator = Paginator(books, size)
    books = paginator.page(page)
    total_page = math.ceil(total / size)
    pages = get_pages(page, total_page)
    b = get_default_book()

    params = {
        'page': page,
        'total': total,
        'total_page': total_page,
        'books': format_books(books),
        'pages': pages,
        'book': b,
        'settings': settings,
        'newest': newest_books(),
        'hottest': hottest_books(),
    }
    return params


def format_books(books):
    if len(books) == 0:
        return books

    res = []
    for b in books:
        res.append(get_data(b))
    return res


def get_chapter(b):
    return Chapter.objects.filter(book_id=b.id).order_by('-id').first()


def search(request):
    search_type = request.GET.get('type')
    keyword = request.GET.get('key')
    if search_type is None or len(search_type) == 0 \
            or keyword is None or len(keyword) == 0:
        return home(request)

    data = []
    if search_type == 'book':
        books = Book.objects.filter(status=0).filter(name__icontains=keyword).all()
        if len(books) > 0:
            for b in books:
                data.append(get_data(b))
    elif search_type == 'author':
        authors = Author.objects.filter(status=0).filter(name__icontains=keyword).all()
        if len(authors) > 0:
            author_ids = []
            for author in authors:
                author_ids.append(str(author.id))
            books = Book.objects.raw('select * from novel_book_authors a left join novel_book b '
                                     'on a.book_id=b.id where a.author_id in("' + '"'.join(author_ids) + '")')
            if len(books) > 0:
                for b in books:
                    data.append(get_data(b))
    else:
        return home(request)

    params = {
        'type': search_type,
        'keyword': keyword,
        'book': get_default_book(),
        'books': data,
        'settings': settings,
    }
    return render_to_response('search.html', params)


def category_list(request, *args, **kwargs):
    categories = Category.objects.all()
    size = 50
    page = Util.get_page(kwargs)
    pinyin = kwargs.get('pinyin')
    category = None
    if pinyin is not None and len(pinyin) > 0:
        category = Category.objects.filter(pinyin=pinyin).first()
    if category is not None:
        books = Book.objects.filter(categories=category).filter(status=0).order_by('-id').all()
    else:
        books = Book.objects.filter(status=0).order_by('-id').all()
    total = books.count()
    paginator = Paginator(books, size)
    books = paginator.page(page)
    total_page = math.ceil(total / size)
    pages = get_pages(page, total_page)
    b = get_default_book()
    params = {
        'settings': settings,
        'book': get_default_book(),
        'category_page': True,
        'books': get_datas(books),
        'category': category,
        'total': total,
        'total_page': total_page,
        'pages': pages,
        'book': b,
        'categories': categories,
        'page': page,
        'hottest': hottest_books(),
        'newest': newest_books(),
    }
    return render_to_response('category.html', params)


def get_datas(books):
    res = []
    for b in books:
        res.append(get_data(b))
    return res


def rank(request, *args, **kwargs):
    books = Book.objects.filter(status=0).order_by('-clicks').all()[:50]
    params = {
        'settings': settings,
        'book': get_default_book(),
        'rank_page': True,
        'books': get_datas(books),
        'hottest': hottest_books(),
        'newest': newest_books(),
    }
    return render_to_response('rank.html', params)


def author_works(request, *args, **kwargs):
    pinyin = kwargs.get('pinyin')
    if pinyin is None:
        return home(request)
    author = Author.objects.filter(pinyin=pinyin).first()
    if author is None:
        return home(request)
    books = Book.objects.filter(authors=author).order_by('-id').all()
    params = {
        'settings': settings,
        'book': get_default_book(),
        'author': author,
        'books': get_datas(books),
    }
    return render_to_response('works.html', params)


def trends(request, *args, **kwargs):
    params = {
        'settings': settings,
        'book': get_default_book(),
        'trend_page': True,
    }
    return render_to_response('trends.html', params)


def subject(request, *args, **kwargs):
    params = {
        'settings': settings,
        'book': get_default_book(),
        'subject_page': True,
    }
    return render_to_response('subject.html', params)


def hottest_books(size=15):
    books = Book.objects.filter(status=0).order_by("-clicks").all()[:size]
    return get_datas(books)


def newest_books(size=15):
    books = Book.objects.filter(status=0).order_by('-id').all()[:size]
    return get_datas(books)


def archives(author):
    books = Book.objects.filter(status=0).filter(authors=author).order_by('-id').all()
    return get_datas(books)


def get_sources(b):
    sources = b.sources.all()
    return sources


def page_not_found(request):
    return home(request)


def server_error(request):
    return home(request)


def contact(request):
    params = {
        'book': get_default_book(),
        'contact_page': True,
    }
    return render_to_response('contact.html', params)
