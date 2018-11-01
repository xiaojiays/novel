import hashlib
import time

from bs4 import BeautifulSoup
from grab import Grab


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
