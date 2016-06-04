#!/usr/bin/python
# codeing:utf-8
# Be hxs
import re
import time
from threading import Thread
try:
    import requests
except ImportError:
    print "import requests error"
    exit(0)


def print_run_time(func):
    """
    装饰器函数，输出运行时间
    """

    def wrapper(self, *args, **kw):
        local_time = time.time()
        # print args),kw
        func(self)
        print 'run time is {:.2f}:'.format(time.time() - local_time)
    return wrapper


class hbk_crawler(object):
    """黑板客爬虫闯关"""

    def __init__(self): pass
    #super(hbk_exxx, self).__init__()

    def login(self, level):
        """登录函数 input:第几关"""
        self.url = 'http://www.heibanke.com/lesson/crawler_ex' + level
        self.login_url = 'http://www.heibanke.com/accounts/login/?next=/lesson/crawler_ex' + level
        self.s = requests.session()
        print u"正在登录第{}关....".format(level)
        try:
            self.csrftoken = self.s.get(self.login_url).cookies['csrftoken']
        except:
            print u"网络连接错误，请重试..."
            exit()
        self.payload = {'username': 'test', 'password': 'test123',
                        'csrfmiddlewaretoken': self.csrftoken}
        self.payload['csrfmiddlewaretoken'] = self.s.post(
            self.login_url, self.payload).cookies['csrftoken']
        print u"登录成功...."
        return None

    @print_run_time
    def ex01(self, *args, **kw):
        """ 第1关:找密码"""
        url = 'http://www.heibanke.com/lesson/crawler_ex00/'
        num = ''
        while True:
            content = requests.get(url + str(num)).text
            pattern = r'<h3>(.*)</h3>'
            result = re.findall(pattern, content)
            try:
                num = int(
                    ''.join(map(lambda n: n if n.isdigit() else '', result[0])))
            except:
                break
            print result[0]
        print result[0]

    @print_run_time
    def ex02(self, *args, **kw):
        """ 第2关：猜密码 """
        url = 'http://www.heibanke.com/lesson/crawler_ex01/'
        payload = {'username': 'test', 'password': 0}
        for n in range(30):
            payload['password'] = n
            content = requests.post(url, payload).text
            pattern = r'<h3>(.*)</h3>'
            result = re.findall(pattern, content)
            print "try enter {} ...".format(n), result[0]
            if u"错误" not in result[0]:
                break

    @print_run_time
    def ex03(self, *args, **kw):
        """ 第3关：猜密码，加入了登录验证,CSRF保护 """
        self.login('02')
        for n in range(30):
            self.payload['password'] = n
            content = self.s.post(self.url, self.payload).text
            pattern = r'<h3>(.*)</h3>'
            result = re.findall(pattern, content)
            print "try enter {} ...".format(n), result[0]
            if u"错误" not in result[0]:
                break

    def parseurl(self, url):
        """分析网页,查找密码位置和值"""
        while self.count < 100:
            response = self.s.get(url)
            if response.ok:
                content = response.text
                pos_pattern = r'_pos.>(.*)</td>'
                val_pattern = r'_val.>(.*)</td>'
                pos_list = re.findall(pos_pattern, content)
                val_list = re.findall(val_pattern, content)
                for pos, val in zip(pos_list, val_list):
                    if pos not in self.pw_dict:
                        self.pw_dict[pos] = val
                        self.count = self.count + 1
                print str(self.count) + '%' + self.count // 2 * '*'

    @print_run_time
    def ex04(self, *args, **kw):
        """ 第4关:找密码,加入了登录验证,CSRF保护,密码长度100位，响应时间增加 """
        self.count = 0
        self.login('03')
        self.pw_dict = {}        
        pw_url = ('http://www.heibanke.com/lesson/crawler_ex03/pw_list',)
        # 线程数,黑板客服务器15秒内最多响应2个请求，否则返回404.
        n = 2
        threads = [Thread(target=self.parseurl, args=(
            pw_url)) for i in xrange(n)]
        for t in threads:
            print t.name, 'start...'
            t.start()
        for t in threads:
            t.join()
        self.pw_list = ['' for n in range(101)]
        for pos in self.pw_dict.keys():
            self.pw_list[int(pos)] = self.pw_dict[pos]
        password = int(''.join(self.pw_list))
        self.payload['password'] = password
        response = self.s.post(self.url, self.payload)
        pattern = r'<h3>(.*)</h3>'
        result = re.findall(pattern, response.text)
        print result[0] 

if __name__ == '__main__':
    Hbk_crawler = hbk_crawler()
    Hbk_crawler.ex01()
    Hbk_crawler.ex02()
    Hbk_crawler.ex03()
    Hbk_crawler.ex04()
