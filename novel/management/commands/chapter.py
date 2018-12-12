import re

from django.core.management.base import BaseCommand

from novel.models import SourceLink, Source, Chapter
from novel.util import Util


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--sid',
            type=int,
            help='同步章节数据',
            default=0,
        )

    def handle(self, *args, **options):
        source_id = options.get('sid')
        if source_id == 0:
            sources = Source.objects.all()
            for source in sources:
                self.chapter(source)
        else:
            self.chapter(Source.objects.filter(id=source_id).first())

    @staticmethod
    def chapter(source):
        if source is None:
            print('source数据错误')
            return

        print('开始同步章节数据')
        print("\t开始同步 " + source.name)

        if source.name == '遮天小说网':
            Command.zhetian(source)
        elif source.name == '顶点小说网':
            Command.dingdian(source)
        elif source.name == '笔趣阁':
            Command.biquge(source)
        elif source.name == '看书中文网':
            Command.kanshu(source)
        elif source.name == '求书网':
            Command.qiushu(source)
        elif source.name == '书荒阁':
            Command.shuhuangge(source)
        elif source.name =='天籁小说':
            Command.tianlai(source)

        print("\t同步 " + source.name + " 完毕")
        print('同步章节数据完毕')

    @staticmethod
    def zhetian(source):
        offset = 0
        size = 100
        pattern = '<a.*?href="(.*?)".*?title="(.*?)">(.*?)</a>'
        links = SourceLink.objects.filter(source_id=source.id).all()[offset:size]
        while len(links) > 0:
            for link in links:
                if link.no_need_grab():
                    continue
                print("\t正在同步\t" + source.name + " 链接：" + link.link)
                soup = Util.get_html_soup(link.link)
                lists = soup.find_all(class_="dirlist")
                if lists is None or len(lists) == 0:
                    print("\t同步\t" + link.link + " 失败")
                    continue
                finds = re.findall(pattern, str(lists[0]))
                number = 1
                for find in finds:
                    status = True
                    number = Command.get_number(find[2], number)
                    chapter = Chapter(title=find[2],
                                      source_id=source.id,
                                      book_id=link.book_id,
                                      link=source.website + find[0],
                                      number=number,
                                      status=status,
                                      )
                    if not Chapter.exists(chapter):
                        chapter.save()
            offset += size
            links = SourceLink.objects.filter(status=0).filter(source_id=source.id).all()[offset:size]

    @staticmethod
    def dingdian(source):
        offset = 0
        size = 100
        links = SourceLink.objects.filter(source_id=source.id).all()[offset:size]
        pattern = '<a.*?href="(.*?)">(.*?)</a>'
        while len(links) > 0:
            for link in links:
                if link.no_need_grab():
                    continue
                print("\t正在同步\t" + source.name + " 链接：" + link.link)
                soup = Util.get_html_soup(link.link)
                lists = soup.find_all('dd')
                if lists is None or len(lists) == 0:
                    print("\t同步\t" + link.link + " 失败")
                    continue
                number = 1
                chapters = []
                history = {}
                for item in lists:
                    finds = re.findall(pattern, str(item))
                    if history.get(finds[0][0]) is not None:
                        for c in chapters:
                            if c['link'] == finds[0][0]:
                                chapters.remove(c)
                    else:
                        history.setdefault(finds[0][0], 1)
                        chapters.append({'link': finds[0][0], 'title': finds[0][1]})

                for c in chapters:
                    number = Command.get_number(c.get('title'), number)
                    chapter = Chapter(title=c.get('title'),
                                      source_id=source.id,
                                      book_id=link.book_id,
                                      link=link.link + c.get('link'),
                                      number=number)
                    if not Chapter.exists(chapter):
                        chapter.save()

            offset += size
            links = SourceLink.objects.filter(status=0).filter(source_id=source.id).all()[offset:size]

    @staticmethod
    def biquge(source):
        offset = 0
        size = 100
        links = SourceLink.objects.filter(source_id=source.id).all()[offset:size]
        pattern = '<a.*?href="(.*?)">(.*?)</a>'
        while len(links) > 0:
            for link in links:
                if link.no_need_grab():
                    continue
                print("\t正在同步\t" + source.name + " 链接：" + link.link)
                soup = Util.get_html_soup(link.link)
                lists = soup.find_all('dd')
                if lists is None or len(lists) == 0:
                    print("\t同步\t" + link.link + " 失败")
                    continue
                number = 0
                chapters = []
                history = {}
                for item in lists:
                    finds = re.findall(pattern, str(item))
                    if history.get(finds[0][0]) is not None:
                        for c in chapters:
                            if c['link'] == finds[0][0]:
                                chapters.remove(c)
                    else:
                        history.setdefault(finds[0][0], 1)
                        chapters.append({'link': finds[0][0], 'title': finds[0][1]})

                for c in chapters:
                    number = Command.get_number(c.get('title'), number)
                    chapter = Chapter(title=c.get('title'),
                                      source_id=source.id,
                                      book_id=link.book_id,
                                      link=link.link + c.get('link'),
                                      number=number)
                    if not Chapter.exists(chapter):
                        chapter.save()

            offset += size
            links = SourceLink.objects.filter(status=0).filter(source_id=source.id).all()[offset:size]

    @staticmethod
    def kanshu(source):
        offset = 0
        size = 100
        links = SourceLink.objects.filter(source_id=source.id).all()[offset:size]
        pattern = '<a.*?href="(.*?)".*?title="(.*?)">.*?</a>'
        while len(links) > 0:
            for link in links:
                if link.no_need_grab():
                    continue
                print("\t正在同步\t" + source.name + " 链接：" + link.link)
                soup = Util.get_html_soup(link.link)
                lists = soup.find_all('li', class_='chapter')
                if lists is None or len(lists) == 0:
                    print("\t同步\t" + link.link + " 失败")
                    continue
                number = 1
                chapters = []
                history = {}
                for item in lists:
                    finds = re.findall(pattern, str(item))
                    if history.get(finds[0][0]) is not None:
                        for c in chapters:
                            if c['link'] == finds[0][0]:
                                chapters.remove(c)
                    else:
                        history.setdefault(finds[0][0], 1)
                        chapters.append({'link': finds[0][0], 'title': finds[0][1]})

                for c in chapters:
                    number = Command.get_number(c.get('title'), number)
                    chapter = Chapter(title=c.get('title'),
                                      source_id=source.id,
                                      book_id=link.book_id,
                                      link=c.get('link'),
                                      number=number)
                    if not Chapter.exists(chapter):
                        chapter.save()

            offset += size
            links = SourceLink.objects.filter(status=0).filter(source_id=source.id).all()[offset:size]

    @staticmethod
    def qiushu(source):
        offset = 0
        size = 100
        links = SourceLink.objects.filter(source_id=source.id).all()[offset:size]
        pattern = '<a.*?href="(.*?)">(.*?)</a>'
        while len(links) > 0:
            for link in links:
                if link.no_need_grab():
                    continue
                print("\t正在同步\t" + source.name + " 链接：" + link.link)
                soup = Util.get_html_soup(link.link)
                contents = soup.find_all('div', class_='book_con_list')
                if contents is None or len(contents) != 2:
                    print("\t同步\t" + link.link + " 失败")
                    continue

                lists = []
                finds = re.findall(pattern, str(contents[1]))
                if finds is not None and len(finds) > 0:
                    for find in finds:
                       lists.append(find)
                if lists is None or len(lists) == 0:
                    print("\t同步\t" + link.link + " 失败")
                    continue

                chapters = []
                history = {}
                for item in lists:
                    if history.get(item[0]) is not None:
                        for c in chapters:
                            if c['link'] == item[0]:
                                chapters.remove(c)
                    else:
                        history.setdefault(item[0], 1)
                        chapters.append({'link': item[0], 'title': item[1]})

                number = 1
                status = True
                for c in chapters:
                    number = Command.get_number(c['title'], number)
                    chapter = Chapter(title=str(c['title']),
                                      source_id=source.id,
                                      book_id=link.book_id,
                                      link=link.link + '/' + str(c['link']),
                                      number=number,
                                      status=status,)
                    if not Chapter.exists(chapter):
                        chapter.save()

            offset += size
            links = SourceLink.objects.filter(status=0).filter(source_id=source.id).all()[offset:size]

    @staticmethod
    def shuhuangge(source):
        offset = 0
        size = 100
        links = SourceLink.objects.filter(source_id=source.id).all()[offset:size]
        pattern = '<a.*?href="(.*?)">(.*?)</a>'
        while len(links) > 0:
            for link in links:
                if link.no_need_grab():
                    continue
                print("\t正在同步\t" + source.name + " 链接：" + link.link)
                soup = Util.get_html_soup(link.link)
                lists = soup.find_all('dd')
                if lists is None or len(lists) == 0:
                    print("\t同步\t" + link.link + " 失败")
                    continue
                number = 1
                chapters = []
                history = {}
                for item in lists:
                    finds = re.findall(pattern, str(item))
                    if history.get(finds[0][0]) is not None:
                        for c in chapters:
                            if c['link'] == finds[0][0]:
                                chapters.remove(c)
                    else:
                        history.setdefault(finds[0][0], 1)
                        chapters.append({'link': finds[0][0], 'title': finds[0][1]})

                for c in chapters:
                    number = Command.get_number(c.get('title'), number)
                    chapter = Chapter(title=c.get('title'),
                                      source_id=source.id,
                                      book_id=link.book_id,
                                      link=source.website + c.get('link'),
                                      number=number)
                    if not Chapter.exists(chapter):
                        chapter.save()

            offset += size
            links = SourceLink.objects.filter(status=0).filter(source_id=source.id).all()[offset:size]

    @staticmethod
    def tianlai(source):
        offset = 0
        size = 100
        links = SourceLink.objects.filter(source_id=source.id).all()[offset:size]
        pattern = '<a.*?href="(.*?)">(.*?)</a>'
        while len(links) > 0:
            for link in links:
                if link.no_need_grab():
                    continue
                print("\t正在同步\t" + source.name + " 链接：" + link.link)
                soup = Util.get_html_soup(link.link)
                lists = soup.find_all('dd')
                if lists is None or len(lists) == 0:
                    print("\t同步\t" + link.link + " 失败")
                    continue
                number = 1
                chapters = []
                history = {}
                for item in lists:
                    finds = re.findall(pattern, str(item))
                    if history.get(finds[0][0]) is not None:
                        for c in chapters:
                            if c['link'] == finds[0][0]:
                                chapters.remove(c)
                    else:
                        history.setdefault(finds[0][0], 1)
                        chapters.append({'link': finds[0][0], 'title': finds[0][1]})

                for c in chapters:
                    number = Command.get_number(c.get('title'), number)
                    chapter = Chapter(title=c.get('title'),
                                      source_id=source.id,
                                      book_id=link.book_id,
                                      link=source.website + c.get('link'),
                                      number=number)
                    if not Chapter.exists(chapter):
                        chapter.save()

            offset += size
            links = SourceLink.objects.filter(status=0).filter(source_id=source.id).all()[offset:size]

    @staticmethod
    def get_number(title, number):
        num = Command.get_num(title)
        if num != -1:
            if num - number > 10 or num < number:
                number += 0
            else:
                number = num
        return number

    @staticmethod
    def get_num(title):
        pattern = "第(\d+)章"
        finds = re.findall(pattern, title)
        if finds is None or len(finds) == 0:
            pattern = "第(.*?)章"
            finds = re.findall(pattern, title)
            if finds is None or len(finds) == 0:
                return -1
            return Command.chinese2digits(str(finds[0]))
        else:
            return int(finds[0])

    @staticmethod
    def chinese2digits(uchars_chinese):
        try:
            common_used_numerals_tmp = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8,
                                    '九': 9, '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}

            total = 0
            r = 1
            for i in range(len(uchars_chinese) - 1, -1, -1):
                val = common_used_numerals_tmp.get(uchars_chinese[i])
                if val >= 10 and i == 0:
                    if val > r:
                        r = val
                        total = total + val
                    else:
                        r = r * val
                elif val >= 10:
                    if val > r:
                        r = val
                    else:
                        r = r * val
                else:
                    total = total + r * val
            return total
        except Exception as e:
            print(e)
        return -100

