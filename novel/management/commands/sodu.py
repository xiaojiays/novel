from django.core.management.base import BaseCommand
from grab import Grab
from bs4 import BeautifulSoup
import re
import time
from novel.models import Book, Chapter, Content
from novel.util import Util


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('mode', nargs='+', type=int)

    def handle(self, *args, **options):
        for mode in options['mode']:
            if mode == 0:
                Command.grab_rank()
            elif mode == 1:
                Command.init_chapter()
            elif mode == 2:
                Command.init_content()

    @staticmethod
    def grab_rank():
        rank_url = 'http://www.sodu.cc/top_{num}.html'
        i = 1
        while i < 9:
            url = rank_url.replace('{num}', str(i))
            print("\t正在抓取：\t" + url)
            i += 1
            Command.grab_rank_data(url)
        print('sodu 点击排行榜数据抓取完毕！')

    @staticmethod
    def grab_rank_data(url):
        body = Command.get_body(url)
        soup = BeautifulSoup(body, 'html.parser')
        div_list = soup.find_all(class_='main-html')
        pattern = "<a.*?href=\"http://www.sodu.cc/mulu_(.*?).html\".*?>(.*?)<\/a>"
        for item in div_list:
            finds = re.findall(pattern, str(item))
            if finds is None or len(finds) != 2 or len(finds[0]) != 2:
                continue
            if Command.book_exists(finds[0][1]):
                continue
            book = Book(name=finds[0][1],
                        category_id=0,
                        created_at=int(time.time()),
                        updated_at=int(time.time()),
                        source='sodu',
                        sid=finds[0][0],
                        status=0)
            book.save()

    @staticmethod
    def book_exists(name):
        return Book.objects.filter(name=name).count() > 0

    @staticmethod
    def init_chapter():
        print("开始初始化章节")
        offset = 0
        size = 100
        books = Book.objects.filter(source='sodu').filter(status=0).all()[offset:size]
        while len(books) > 0:
            for book in books:
                Command.grab_book_chapter(book)
            offset += size
            books = Book.objects.filter(source='sodu').filter(status=0).all()[offset:size]
        print("章节初始化完毕！")

    @staticmethod
    def grab_book_chapter(book):
        max_page = Command.get_max_page(book)
        if max_page == 0:
            return

        while max_page > 0:
            chapter_url = 'http://www.sodu.cc/mulu_' + book.sid + '_' + str(max_page) + '.html'
            print("\t正在采集 " + book.name + " 第 " + str(max_page) + " 页\t" + chapter_url)
            body = Command.get_body(chapter_url)
            soup = BeautifulSoup(body, 'html.parser')
            html_list = soup.find_all(class_='main-html')
            html_list.reverse()
            pattern = '<a.*?alt="(.*?)".*?href="(.*?)".*?>(.*?)</a>[\s\S]*?<a.*?href="(.*?)".*?>(.*?)</a>[\s\S]' \
                      '*?<div.*?>(.*?)</div>'
            for item in html_list:
                item = str(item)
                finds = re.findall(pattern, item)
                chapter = Chapter(title=Command.format_title(finds[0][0]),
                                  link=Command.get_link(finds[0][1]),
                                  source=finds[0][4],
                                  book_id=book.id,
                                  updated_at=Util.str_to_time(finds[0][5], '%Y/%m/%d %H:%M:%S'),
                                  created_at=int(time.time()))
                if Command.chapter_not_exists(chapter):
                    chapter.save()
            max_page -= 1
            time.sleep(1)

    @staticmethod
    def get_max_page(book):
        chapter_url = 'http://www.sodu.cc/mulu_' + book.sid + '.html'
        body = Command.get_body(chapter_url)
        soup = BeautifulSoup(body, 'html.parser')
        page_input = soup.find(class_='pager')
        pattern = '共.*?(\d+).*?页'
        finds = re.findall(pattern, str(page_input))
        if len(finds) == 1:
            return int(finds[0])
        else:
            print("获取 " + book.name + " 总页数失败")
            return 0

    @staticmethod
    def get_body(url):
        g = Grab()
        g.setup(headers=Command.get_headers())
        resp = g.go(url)
        return resp.body

    @staticmethod
    def get_headers():
        return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/69.0.3497.100 Safari/537.36',
                'Referer': 'http://www.sodu.cc/top.html'}

    @staticmethod
    def get_link(url):
        return url.split('chapterurl=')[1]

    @staticmethod
    def format_title(title):
        return title.replace('【卓雅居全文字秒更】', '').strip()

    @staticmethod
    def chapter_not_exists(chapter):
        return Chapter.objects.filter(source=chapter.source).filter(title=chapter.title).count() == 0

    @staticmethod
    def init_content():
        print(1)

