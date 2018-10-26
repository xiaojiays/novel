import re
import json

from django.core.management.base import BaseCommand

from novel.models import SourceLink, Source, Chapter
from novel.util import Util


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--init',
            type=int,
            help='初始化章节数据',
        )

    def handle(self, *args, **options):
        if options.get('init') is not None:
            self.init_data(options.get('init'))

    @staticmethod
    def init_data(source_id):
        offset = 0
        size = 100
        source = Source.objects.filter(id=source_id).first()
        if source is None:
            print('初始化参数错误')
            return

        print('开始初始化章节数据')

        pattern = '<a.*?href="(.*?)".*?title="(.*?)">(.*?)</a>'
        links = SourceLink.objects.filter(status=0).filter(source_id=source_id).all()[offset:size]
        while len(links) > 0:
            for link in links:
                print("\t正在初始化\t" + link.link)
                soup = Util.get_html_soup(link.link)
                lists = soup.find_all(class_="dirlist")
                if lists is None or len(lists) == 0:
                    print("\t初始化\t" + link.link + " 失败")
                    continue
                finds = re.findall(pattern, str(lists[0]))
                for find in finds:
                    chapter = Chapter(title=find[2],
                                      source_id=source_id,
                                      book_id=link.book_id,
                                      link=source.website + find[0],
                                      )
                    if not Chapter.exists(chapter):
                        content_id = Command.grab_content(source, chapter)
                        if content_id == 0:
                            break
                        chapter.content_id = content_id
                        chapter.save()
                    break
                link.status = 1
                #link.save()
            offset += size
            links = SourceLink.objects.filter(status=0).filter(source_id=source_id).all()[offset:size]

        print('初始化章节数据结束')

    @staticmethod
    def grab_content(source, chapter):
        soup = Util.get_html_soup(chapter.link)
        title = soup.find(class_='title')
        title_pattern = '<span>.*?更新时间：(.*?)</span>'
        finds = re.findall(title_pattern, str(title))
        if len(finds) != 1:
            print("\t获取章节内容\t" + chapter.title + " 失败 \t" + chapter.link)
            return 0
        chapter.updated_at = Util.str_to_time(finds[0], '%Y-%m-%d %H:%M:%S')

        content_pattern = "\$\.get\('(.*?)'"

        finds = re.findall(content_pattern, str(soup))
        if len(finds) != 1:
            print("\t获取章节内容\t" + chapter.title + " 失败 \t" + chapter.link)
            return 0

        body = Util.get_html(source.website + finds[0])
        json_obj = json.loads(body)
        return 0
