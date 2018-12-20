# -*- coding: UTF-8 -*-
import hashlib
import time
import re
import urllib
import uuid

from bs4 import BeautifulSoup
from grab import Grab

from novel import settings


class Util:

    @staticmethod
    def md5(s):
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    @staticmethod
    def str_to_time(s, f):
        return int(time.mktime(time.strptime(s, f)))

    @staticmethod
    def get_html_soup(url):
        g = Grab()
        g.setup(headers=Util.get_headers())
        resp = g.go(url)
        return BeautifulSoup(resp.body, 'html.parser')

    @staticmethod
    def get_html(url):
        g = Grab()
        g.setup(headers=Util.get_headers())
        resp = g.go(url)
        return resp.body

    @staticmethod
    def get_headers():
        return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko)'
                              'Chrome/69.0.3497.100 Safari/537.36',
                'Referer': ''}

    @staticmethod
    def get_page(kwargs):
        if kwargs.get('page') is None:
            return 1
        return int(kwargs.get('page'))

    @staticmethod
    def get_number(title, number):
        num = Util.get_num(title)
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
            return Util.chinese2digits(str(finds[0]))
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

    @staticmethod
    def download_img(img_url):
        path = 'images/' + str(uuid.uuid1()) + '.' + img_url.split('.')[-1]
        local = settings.MEDIA_ROOT + '/' + path
        urllib.request.urlretrieve(img_url, local)
        return path
