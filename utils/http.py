# -*- coding: utf-8 -*-
# Project = https://github.com/super-l/superl-url.git
'''
    程序基础功能模块
    Created by superl[N.S.T].         忘忧草安全团队(Nepenthes Security Team)
                                                                      00000
                                                                      00000
                                                                      00000
      00000000    00000  00000  00000000000     00000000    000000000 00000
     00000000000  00000  00000  000000000000   00000000000  000000000 00000
     00000  000   00000  00000  000000 00000  000000 00000  00000000  00000
     000000000    00000  00000  00000   0000  0000000000000 000000    00000
      0000000000  00000  00000  00000   00000 0000000000000 00000     00000
         0000000  00000  00000  00000   00000 00000         00000     00000
     00000  0000  000000000000  000000000000  000000000000  00000     00000
     00000000000  000000000000  000000000000   00000000000  00000     00000
      000000000   0000000000    00000000000     00000000    00000     00000
                                00000
                                00000                   Blog:www.superl.org
                                00000
'''
import sys
import gzip
import random
from io import StringIO
try:
    import urllib2
except ImportError:
    import urllib.request

def getheaders():
    user_agent_list=[]
    f = open(__file__+'/../user-agent-list.txt')  # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    while line:
        line=line.replace('\n','')
        user_agent_list.append(line)
        line = f.readline()
    f.close()
    UserAgent=random.choice(user_agent_list)

    return UserAgent
UserAgent=getheaders()

HEADERS = {
		  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
          'X-Requested-With': 'XMLHttpRequest',
          'User-Agent': UserAgent,
          'Referer': 'https://www.jianshu.com',
          'Accept-Language': 'zh-CN,zh;q=0.9',
          'Host': 'videocdn.dlyilian.com:8091'

}
proxy='182.35.82.64:9999'  #使用本地代理
#proxy='username:password@123.58.10.36:8080'  #购买代理
proxies={
    'http':'http://'+proxy,
    'https':'https://'+proxy
}
# 获取网页内容
def get_html_content(target_url,stream=False):
    send_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': UserAgent,
        'Referer': 'https://www.jianshu.com',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    try:
        if sys.version > '3':
            req = urllib.request.Request(target_url, headers=send_headers,stream=stream)
            response = urllib.request.urlopen(req, timeout=20)
            if (response.headers.get('content-encoding', None) == 'gzip'):
                html = gzip.GzipFile(
                    fileobj=StringIO(response.read())).read()
                return html

        else:
            req = urllib2.Request(target_url, headers=send_headers,stream=stream)
            response = urllib2.urlopen(req, timeout=30)
            # print get_request.info()

        return response.read().decode('utf-8')

    except Exception as e:
        print("请求失败:%s"%(e))