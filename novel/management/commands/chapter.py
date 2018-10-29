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
                    chapter = Chapter(title=find[2],
                                      source_id=source.id,
                                      book_id=link.book_id,
                                      link=source.website + find[0],
                                      number=number,
                                      )
                    if not Chapter.exists(chapter):
                        chapter.save()
                    number += 1
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
                number = 0
                for item in lists:
                    finds = re.findall(pattern, str(item))
                    chapter = Chapter(title=finds[0][1],
                                      source_id=source.id,
                                      book_id=link.book_id,
                                      link=link.link + finds[0][0],
                                      number=number)
                    if not Chapter.exists(chapter):
                        chapter.save()
                    number += 1

            offset += size
            links = SourceLink.objects.filter(status=0).filter(source_id=source.id).all()[offset:size]
