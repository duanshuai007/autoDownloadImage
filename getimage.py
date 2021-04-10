#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import re
import os
import time
import urllib.request
import threading
import queue
import json
import random
import chardet

import imageJson
from logger import LoggingProducer

class getimage():
    win_queue = None
    def __init__(self, window_queue):
        self.queue = queue.Queue(5)
        self.win_queue = window_queue
        self.iJson = imageJson.imageJson()
        self.logger = LoggingProducer().get_default_logger()
        thread = threading.Thread(target=self.downloadThread, args=[])
        thread.setDaemon(True)
        thread.start()

    def getHtml(self, url):
        self.logger.info("gethtml:%s" % url)
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        try:
            req = urllib.request.Request(url=url, headers=headers)
            page = urllib.request.urlopen(req)
            html = page.read()
            encodingtype = chardet.detect(html)
            return [encodingtype, html]
        except Exception as e:
            self.logger.error("getHtml error:{}".format(e))
            for val in e.args:
                if val == "timed out":
                    self.win_queue.put(self.iJson.generateErrorJson("open url timeout"))
            return []

    def start(self, html, saveimagepath):
        try:
            self.logger.info("html={} savepath={}".format(html, saveimagepath))
            if not self.queue.full():
                self.queue.put([html, saveimagepath])
        except Exception as e:
            self.logger.error("start error:{}".format(e))

    #因为这个网站一个页面就一张大图片，所以每次都需要打开下一个页面，获取下一个图片地址
    def findImageUrl(self, htmlstr):
        #reg = r'<img class="img-fluid" src.*?="([.*\S]*?\.(?:jpg|png|jpeg|gif))" />'
        reg = r'src.*?="(http[.*\S]*?\.(?:jpg|png|jpeg|gif))"'
        imgre = re.compile(reg)
        imgurllist = re.findall(imgre, htmlstr)
        self.logger.info("find image url:{}".format(imgurllist))
        return imgurllist
        
    def getImageTitle(self, htmlstr):
        res = ''
        reg = r'<title>(.*)</title>'
        imgre = re.compile(reg)
        imglist = re.findall(imgre, htmlstr)        
        res = str(imglist[0])
        self.logger.info("res={}".format(res))  
        res = re.sub(r'[?*<>"|\\/:]*', '', res)
        self.logger.info("title={}".format(res))
        res = res.replace(' ', '')
        self.logger.info("title={}".format(res))
        if len(res) > 40:
            res = res[:40]
        return res

    def downloadThread(self):
        while True:
            try:
                time.sleep(0.2)
                if not self.queue.empty():
                    item_list = self.queue.get()
                    imageUrl = item_list[0]
                    savedir = item_list[1]
                    self.logger.info("imageUrl : {}".format(imageUrl))
                    #先读取页面，得到页面内容和编码信息
                    listres = self.getHtml(imageUrl)
                    if len(listres) != 2:
                        self.logger.error("get html error")
                        self.win_queue.put(self.iJson.generateErrorJson("get html error"))
                        continue
                    html = listres[1]
                    encodemsg = listres[0]
                    if not html:
                        self.logger.error("cant open html")
                        self.win_queue.put(self.iJson.generateErrorJson("can not open html"))
                        continue
                        
                    self.logger.info("the web coding: %s" % listres[0])
                    html = html.decode(encodemsg["encoding"])
                    #self.logger.info(html)
                    #通过网页内容获取文件夹名字，并检测文件创建文件夹
                    imgGroupTitle = self.getImageTitle(html)
                    curImageSaveDir = "{}/{}".format(savedir, imgGroupTitle)
                    self.logger.info("self.saveDir : {}".format(savedir))
                    self.logger.info("curImageSaveDir : {}".format(curImageSaveDir))
                    if not os.path.exists(curImageSaveDir):
                        os.mkdir(curImageSaveDir)
                    self.logger.info("save in:{}".format(curImageSaveDir))
                    #从html页面内容中搜索满足条件的url
                    image_url_list = self.findImageUrl(html)
                    if not image_url_list:
                        self.logger.error("cant find image")
                        continue
                    imgNo = 0
                    imgTotal = len(image_url_list)
                    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
                    #向主窗口发送等待下载图片的数量
                    self.win_queue.put(self.iJson.generateStartJson(None, imgTotal))
                    for imgurl in image_url_list:
                        imgtype = imgurl.split('.')[-1]
                        self.logger.info("download:url={} type={}".format(imgurl, imgtype))
                        self.win_queue.put(self.iJson.generateDownloadJson(imgurl, imgNo, int(imgNo*100/imgTotal), 0, "download start"))
                        timeoutCount = 0
                        filename = "{}//{}.{}".format(curImageSaveDir, imgNo, imgtype)
                        if os.path.exists(filename) == False:
                            while True:
                                req = urllib.request.Request(url=imgurl, headers=headers)
                                with open(filename, 'wb') as f:
                                    try:
                                        #self.logger.info("image url request urlopen")
                                        res = urllib.request.urlopen(req, timeout = 10)
                                        if res:
                                            #self.logger.info("image url request urlopen success, start save")
                                            data = res.read()
                                            f.write(data)
                                            #self.logger.info("save success!!!")
                                            imgNo += 1
                                            self.win_queue.put(self.iJson.generateDownloadJson(imgurl, imgNo, int(imgNo*100/imgTotal), 0, "download ok"))
                                            break
                                        else:
                                            self.logger.error("image url request urlopen failed")
                                    except Exception as e:
                                        self.logger.error("download image error:{}".format(e))
                                        for val in e.args:
                                            if val == 'timed out':
                                                timeoutCount = timeoutCount + 1
                                                if timeoutCount > 5:
                                                    self.curPageFailed = self.curPageFailed + 1
                                                    self.win_queue.put(self.iJson.generateDownloadJson(imgurl, self.ImageDLOKCount, int(imgNo*100/imgTotal), self.curPageFailed, "download error"))
                                                    break
                        else:
                            self.logger.info("file:{} exists".format(filename))
                            imgNo += 1
                            self.win_queue.put(self.iJson.generateDownloadJson(imgurl, imgNo, int(imgNo*100/imgTotal), 0, "download ok"))
                        time.sleep(random.randint(1,3))
            except Exception as e:
                self.logger.error("error:{}".format(e))
                
if __name__ == '__main__':
    pass