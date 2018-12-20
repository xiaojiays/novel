# -*- coding: UTF-8 -*-
import re
import time

from django.core.management.base import BaseCommand

from novel.models import SourceLink, Source, Chapter, Category, Author, Book
from novel.util import Util


class Command(BaseCommand):

    def handle(self, *args, **options):
        source = Source.objects.filter(name='遮天小说网').first()
        if source is None:
            print('source数据错误')
            return

        print("\t开始同步 " + source.name)
        self.zhetian(source)
        print("\t同步 " + source.name + " 完毕")

    def zhetian(self, source):
        link = 'https://www.zhetian.org/top/lastupdate/{page}.html'
        page = 2
        soup = Util.get_html_soup(link.replace('{page}', str(page)))
        pattern = '<a.*?href="(.*?)".*?title="(.*?)".*?>(.*?)</a>'
        while soup is not None:
            finds = soup.find_all("li", class_='headerhui')
            for find in finds:
                matches = re.findall(pattern, str(find))
                if matches is None or len(matches) != 4:
                    continue
                category_name = matches[0][2]
                category = self.get_category(category_name)
                author_name = matches[3][2]
                author = self.get_author(author_name)
                source_link = source.website + matches[1][0]
                book_name = matches[1][1]
                book = Book.objects.filter(name=book_name).first()

                if book is None or book.img is None or len(str(book.img)) == 0:
                    if book is None:
                        book = self.create_book(book_name, author, category, source, source_link)
                    try:
                        self.init_chapters(book, source, source_link)
                    except Exception as e:
                        print(e)
                else:
                    number = self.get_number(book.id, source.id)
                    title = matches[2][2]
                    number = Util.get_number(title, number)
                    chapter = Chapter(title=title,
                                      source_id=source.id,
                                      book_id=book.id,
                                      link=source.website + matches[2][0],
                                      number=number,
                                      status=True)
                    if not Chapter.exists(chapter):
                        chapter.save()

            page += 1
            soup = None

    def get_category(self, category_name):
        category = Category.objects.filter(name=category_name).first()
        if category is not None:
            return category

        category = Category(name=category_name,
                            status=0,
                            parent_id=0)
        category.save()
        return category

    def get_author(self, author_name):
        author = Author.objects.filter(name=author_name).first()
        if author is not None:
            return author

        author = Author(name=author_name,
                        status=0)
        author.save()
        return author

    def create_book(self, book_name, author, category, source, link):
        book = Book(name=book_name, status=0)
        book.save()

        book.authors.add(author)
        book.categories.add(category)
        book.save()

        source_link = SourceLink(book_id=book.id,
                                 source_id=source.id,
                                 link=link)
        source_link.save()
        return book

    def get_number(self, book_id, source_id):
        chapter = Chapter.objects.filter(book_id=book_id, source_id=source_id).order_by('-number').first()
        if chapter is None:
            return 1
        return chapter.number

    def init_chapters(self, book, source, source_link):
        print("开始同步 " + book.name)
        soup = Util.get_html_soup(source_link)

        desc = soup.find(id="intro")
        pattern = '<p>([\s\S]*?)</p>'
        finds = re.findall(pattern, str(desc))
        book.description = str(finds[0])

        imgs = soup.find_all("img")
        if imgs is None or len(imgs) != 2:
            print("\t同步\t" + source_link + " 失败")
            return

        pattern = '<img.*?src="(.*?)"'
        finds = re.findall(pattern, str(imgs[1]))
        if finds is None or len(finds) == 0:
            print("\t同步\t" + source_link + " 失败")
            return

        img = Util.download_img(str(finds[0]))
        book.img = img
        book.save()

        lists = soup.find_all(class_="dirlist")
        if lists is None or len(lists) == 0:
            print("\t同步\t" + source_link + " 失败")
            return

        pattern = '<a.*?href="(.*?)".*?title="(.*?)">(.*?)</a>'
        finds = re.findall(pattern, str(lists[0]))
        number = 1
        chapter_list = []
        for find in finds:
            status = True
            title = str(find[2])
            number = Util.get_number(title, number)
            chapter = Chapter(title=title,
                              source_id=source.id,
                              book_id=book.id,
                              link=source.website + str(find[0]),
                              number=number,
                              status=status,
                              )
            if not Chapter.exists(chapter):
                chapter_list.append(chapter)
                if len(chapter_list) >= 100:
                    Chapter.objects.bulk_create(chapter_list)
        print("同步 " + book.name + " 完毕")

        time.sleep(1)
