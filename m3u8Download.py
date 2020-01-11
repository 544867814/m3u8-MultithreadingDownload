# -*- coding: UTF-8 -*-
import getopt
import sys
import os
import re
import time
import platform
import requests
import datetime
from pathlib import Path
from Crypto.Cipher import AES
from collections import OrderedDict
from queue import Queue
import threading


HEADERS = {
          'X-Requested-With': 'XMLHttpRequest',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
          'Referer': 'https://www.baidu.com/',
          'Accept-Language': 'zh-CN,zh;q=0.8,ja;q=0.6'
}
class BSDownImg(threading.Thread):
    """
    下载图片的消费者
    """
    def __init__(self, page_queue,product_queue,key,download_path, daemon=None):
        super(BSDownImg, self).__init__(daemon=daemon)
        self.page_queue = page_queue
        self.key=key
        self.download_path=download_path
        self.product_queue=product_queue
        self._stop_event = threading.Event()
    def run(self):
        while True:
            if self.product_queue.empty():
                merge_file(self.download_path)
                break
            page=self.page_queue.get()
            self.downloadM3u8(page,self.key,self.download_path)

    def downloadM3u8(self,line,key,download_path):
        """ 根据file_line下载m3u8文件 """
        c_fule_name,pd_url=line
        print("开始下载:%s"%pd_url)
        res = requests.get(pd_url,headers=HEADERS)
        res.encoding = "utf-8"
        try:
            if len(key):  # AES 解密
                with open(os.path.join(download_path, c_fule_name), 'ab') as f:
                    cryptor = AES.new(key, AES.MODE_CBC, key)
                    text = cryptor.decrypt(res.content)
                    f.write(text)
            else:
                with open(os.path.join(download_path, c_fule_name), 'ab') as f:
                    #f.write(res.content)
                    for chunk in res.iter_content(chunk_size=512):
                        if chunk:
                            f.write(chunk)
            self.product_queue.get()
        except ValueError:
            # with open(os.path.join(download_path, "error.txt"), 'ab') as f:
            #     f.write(res.content)
            #     f.write("\n")
            pass

def merge_file(path):
    """
    兼容windows和linux
    :param path:
    :return:
    """
    os.chdir(path)
    plat_f = platform.system()
    if "Win" in plat_f:
        str1 = ""
        for s in checkDownloadFolder(path):
            str1 += s + "+"
        try:
            if (str1[-1] == '+'):
                str1 = str1[:-1]
        except:
            return ''
        path = path.replace('/', '\\')
        # cmd = f"copy /b {path}\*.ts new.tmp"

        cmd = f"copy /b {str1} {path}\\new.tmp"
        os.system(cmd)
        if(os.path.exists(f"{path}\\new.tmp")):
            os.system('del /Q *.ts')
                # os.system('del /Q *.mp4')
            os.rename(f"{path}\\new.tmp", f"{path}\\new.mp4")
            print("合并完成")
            os._exit(0)
            return True

        else :
            print("合并失败")


    elif "Dar" in plat_f:
        str1 = ""
        for s in checkDownloadFolder(path):
            str1 += s + " "
        cmd = f'cat {str1} > new.mp4'
        os.system(cmd)
        os.system('rm -f *.ts')
        os.rename("new.mp4", "new.ts")
        os.system(f'cat new.ts > new.mp4')


def checkDownloadFolder(download_path, ty=".ts"):
    """ 返回下载目录中的文件list """
    temp = []
    try:
        temp += [os.path.abspath(p) for p in Path(download_path).glob(f'**/*{ty}')]
    except PermissionError:
        pass

    def sortNum(name):
        num = "0"
        for n in name:
            if n.isdigit():
                num += n
        return int(num)

    return sorted(temp, key=sortNum)


def testRequest(pd_url):
    """ 测试m3u8文件是否可以正常下载 """
    res = requests.get(pd_url,headers=HEADERS)
    if b"404 Not Found" in res.content:
        return False
    return True


def getFileLine(url):


    """ 获取file_url, 即所有m3u8文件的url地址 """

    all_content = requests.get(url, headers=HEADERS).text  # 获取第一层M3U8文件内容

    http = r'((http|ftp|https)://(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})))'
    url_head = re.findall(http, url)[0][0]

    if "#EXTM3U" not in all_content:
        raise BaseException("非M3U8的链接")



    if "EXT-X-STREAM-INF" in all_content:  # 第一层
        file_line = all_content.split("\n")
        for line in file_line:
            if '.m3u8' in line:
                url = url_head + line  # 拼出第二层m3u8的URL
                all_content = requests.get(url).text

    file_line = all_content.split("\n")
    begin, flag = True, 0
    res_ = OrderedDict()
    key = ""
    list = []
    page_queue = Queue(10000)
    product_queue = Queue(10000)
    n=1
    for index in range(len(file_line)):  # 第二层
        line = file_line[index]
        print(line)
        if "#EXT-X-KEY" in line:  # 找解密Key
            method_pos = line.find("METHOD")
            comma_pos = line.find(",")
            method = line[method_pos:comma_pos].split('=')[1]
            print("Decode Method：", method)

            uri_pos = line.find("URI")
            quotation_mark_pos = line.rfind('"')
            key_path = line[uri_pos:quotation_mark_pos].split('"')[1]

            key_url = url.rsplit("/", 1)[0] + "/" + key_path  # 拼出key解密密钥URL
            res = requests.get(key_url)
            key = res.content
            print("key：", key)

        if "EXTINF" in line:  # 找ts地址并下载
            if "http" in file_line[index + 1]:
                pd_url = file_line[index + 1]
            else:
                pd_url1 = url.rsplit("/", 1)[0] + "/" + file_line[index + 1]  # 拼出ts片段的URL
                pd_url2 = url_head + "/" + file_line[index + 1]  # 拼出ts片段的URL
                if begin and testRequest(pd_url1):
                    flag = 1
                    begin = False
                elif begin and testRequest(pd_url2):
                    flag = 2
                    begin = False
                #
                pd_url = pd_url1 if flag == 1 else pd_url2
            key_path=u"%s.ts"%n
            n=n+1
            page_queue.put((key_path,pd_url))
            product_queue.put((key_path,pd_url))
            # list.append(pd_url)
            # c_fule_name = file_line[index + 1].rsplit("/", 1)[-1]
            # res_[c_fule_name] = pd_url
    return key,page_queue,product_queue


def createDownloadFolder(download_path):
    """ 创建下载目录 """
    # if not os.path.exists(download_path):
    #     os.mkdir(download_path)

    # # 新建日期文件夹
    download_path = os.path.join(download_path) + "/" + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    return download_path

if __name__ == "__main__":
    theread=3 #默认线程数
    document = "" #保存路径
    url = "" #下载地址
    opts, args = getopt.getopt(sys.argv[1:], "u:d:t:")
    if opts:
        for k, v in opts:
            if k == "-u":
                url = v
            if k == "-d":
                document = v
            if k == "-t":
                theread = v
    if document:
        download_dir = document
    else:
        download_dir = os.getcwd() + "/download"

    start = time.time()
    # merge = ""
    # 测试m3u8
    # url = "https://up.imgupio.com/demo/birds.m3u8"
    # #url="https://cdn-5.haku99.com/hls/2019/05/20/UZWZ2mEs/playlist.m3u8"
    # url="https://youku.cdn7-okzy.com/20200101/16484_79e74112/index.m3u8"
    # download_dir = "d:/backup"
    # url="https://youku.cdn7-okzy.com/20200101/16484_79e74112/1000k/hls/index.m3u8"
    download_path=createDownloadFolder(download_dir)
    #"python m3u8Download.py -u https://youku.cdn7-okzy.com/20200101/16484_79e74112/1000k/hls/index.m3u8 -d d:/backup -t 102"
    if not url:
        print("请输入下载地址")
    else:
        url = url.split("url=")[-1]
        print(f"开始下载，m3u8文件地址为：{url}")
        key,page_queue,product_queue = getFileLine(url)
    tsk=[]
    # # 8.构建 50 个消费者来下载图片
    for x in range(0, int(theread)):
        t = BSDownImg(page_queue,product_queue,key,download_path)
        t.daemon=True
        t.start()
        tsk.append(t)
    for tt in tsk:
        tt.join()
    end = time.time()
    print(end-start)

    # merge_file(download_path)
