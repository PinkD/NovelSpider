import re
import socket

import time
from concurrent.futures import ThreadPoolExecutor

import os

from db import DatabaseHelper
from config import BASE_URL, PAGE

import urllib.request

from novel import Novel

USER_AGENT = 'Mozilla/5.0 (Linux; Android 7.0; STF-AL10 Build/HUAWEISTF-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043508 Safari/537.36 V1_AND_SQ_7.2.0_730_YYB_D QQ/7.2.0.3270 NetType/4G WebP/0.3.0 Pixel/1080'


class NovelSpider:
    def __init__(self):
        self._db = DatabaseHelper('novels')
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
        self._opener.addheaders.clear()
        self._opener.addheaders.append(('User-Agent', USER_AGENT))
        self.retry_times = 5
        self.log_file = open('status.log', 'w')
        socket.setdefaulttimeout(10)
        self._pool = ThreadPoolExecutor()
        if not os.path.exists('novels'):
            os.mkdir('novels', 0o755)

    @staticmethod
    def process_novel(self, novel: Novel, url: str):
        retry_time = 0
        while retry_time < self.retry_times:
            try:
                result = self._opener.open(url).read().decode()
            except Exception as e:
                print(e)
                continue
            # print(novel)
            novel.count = int(re.findall('<div>&nbsp;总字数：([0-9]*?)</div>', result).pop())
            novel.type = re.findall('<div>类别：<a href="/wapsort/[0-9]*?_[0-9]*?\.html" title=".*?">(.*?)</a></div>', result).pop()
            page = BASE_URL + re.findall('<a href="(/novel/[0-9]*?/[0-9]*?\.html)" title="' + PAGE + '">1</a>', result).pop()
            max_page = int(re.findall('<span style="color:#666;font-size:11px;line-height: 22px;">共([0-9]*?)章节</span>', result).pop())
            # print(page)
            result = self._opener.open(page).read().decode()
            with open('novels/%d_%s.txt' % (novel.id, novel.title), 'w') as f:
                try:
                    for i in range(1, max_page - 1):
                        content = re.findall('<div id="nr1" style="font-size:18px;">([\s\S]*?)</div>', result).pop().replace('</p>\r\n<p></p>', '').replace('<p>', '').replace('</p>', '').replace('&nbsp;', ' ')
                        # print(content)
                        print('%s->%d/%d' % (novel.title, i, max_page))
                        f.write(content)
                        page = re.findall('<td class="next"><a id="pt_next" href="(' + BASE_URL + '/novel/[0-9]*?/[0-9]*?\.html)">下一章</a></td>', result).pop()
                        # print(page)
                        result = self._opener.open(page).read().decode()
                        time.sleep(1)
                    self._db.insert_novel(novel)
                    print(novel.title + ' Done')
                    self.log_file.write(novel.title + ' Done')
                    return
                except Exception as e:
                    print(e)
            retry_time += 1
        print("!!!Fail to save %s" % novel.title)
        self.log_file.write("!!!Fail to save %s" % novel.title)

    def start(self):
        result = self._opener.open(BASE_URL + '/wapsort/11_1.html').read().decode()
        max_page = int(re.findall('<input style="width: 50%;" type="number" name="page" value="" id="go_page" min="1" max="([0-9]*?)" />', result).pop())
        # max_page = 5
        for i in range(1, max_page):
            result = self._opener.open(BASE_URL + '/wapsort/11_%d.html' % i).read().decode()
            ids = re.findall('<h3><a href="' + BASE_URL + '/novel/([0-9]*)\.html">.*?</a></h3>', result)
            titles = re.findall('<h3><a href="' + BASE_URL + '/novel/[0-9]*\.html">(.*?)</a></h3>', result)
            urls = re.findall('<h3><a href="(' + BASE_URL + '/novel/[0-9]*\.html)">', result)
            authors = re.findall('<p>作者：<strong>(.*?)</strong></p>', result)
            descriptions = re.findall('<span class="abstract"><a href="' + BASE_URL + '/novel/[0-9]*\.html">([\s\S]*?)</a></span>', result)
            for j in range(0, titles.__len__()):
                novel = Novel(titles[j], authors[j], descriptions[j], id=int(ids[j]))
                if self._db.check_novel_exists(novel.id):
                    print("Skip existing: %s" % novel.title)
                    continue
                self._pool.submit(self.process_novel, self, novel, urls[j])
