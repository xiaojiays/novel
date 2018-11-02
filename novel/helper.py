from novel.models import Chapter


def get_categories(books):
    categories = {}
    for book in books:
        category_list = book.categories.all()
        if category_list is None or len(category_list) == 0:
            categories.setdefault(book.id, '')
        else:
            categories.setdefault(book.id, category_list[0].name)
    return categories


def get_chapters(books):
    chapters = {}
    for book in books:
        chapter = Chapter.objects.filter(book_id=book.id).order_by('-id').first()
        if chapter is not None:
            chapters.setdefault(book.id, chapter)
    return chapters


def get_authors(books):
    authors = {}
    for book in books:
        author = book.authors.first()
        if author is not None:
            authors.setdefault(book.id, author)
    return authors
