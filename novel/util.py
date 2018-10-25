import hashlib
import time


class Util:

    @staticmethod
    def md5(s):
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    @staticmethod
    def str_to_time(str, format):
        return int(time.mktime(time.strptime(str, format)))
