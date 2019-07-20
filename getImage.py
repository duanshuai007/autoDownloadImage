#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re
import time
import urllib.request
import logging
import threading
import queue
import json
import random

import imageJson

class getimage():
    win_queue = ''
    curPageUrl = ''
    curPageImageTotalNum = 0
    curImageUrl = ''
    ImageDLOKCount = 0
    curPageFailed = 0
    saveDir = ''

    def __init__(self, window_queue):
        self.queue = queue.Queue(5)
        self.win_queue = window_queue
        self.iJson = imageJson.imageJson()
        thread = threading.Thread(target=self.downloadThread, args=[])
        thread.setDaemon(True)
        thread.start()

    def getHtml(self, url):
        logging.info("gethtml:%s" % url)
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        try:
            req = urllib.request.Request(url=url, headers=headers)
            page = urllib.request.urlopen(req)
            html = page.read()
            logging.info("read html")
            return html
        except Exception as e:
            logging.error("get html error")
            logging.error(e.args)
            for val in e.args:
                if val == "timed out":
                    self.win_queue.put(self.iJson.generateErrorJson("open url timeout"))

    def start(self, html, saveimagepath):
        #logging.info("start!")
        self.saveDir = saveimagepath
        if not self.queue.full():
            self.queue.put(html)

    def getImageList(self, htmlstr):
        #logging.info("get image list")
        reg = r'src.*?="(http[.*\S]*?\.(?:jpg|png|jpeg))"'
        #reg = r'src="([.*\S]*\.jpeg)"'
        imgre = re.compile(reg)
        imglist = re.findall(imgre, htmlstr)
        return imglist

    def downloadThread(self):
        while True:
            time.sleep(0.5)
            if not self.queue.empty():
                msg = self.queue.get()
                self.curPageUrl = msg
                html = self.getHtml(msg)
                if not html:
                    logging.error("cant open html")
                    self.win_queue.put(self.iJson.genarateErrorJson("cant open html"))
                    continue
                html = html.decode('UTF-8')

                imglist = self.getImageList(html)
                if not imglist:
                    logging.error("cant find image")
                    self.win_queue.put(self.iJson.generateErrorJson("cant find imgurl"))
                    continue
                logging.info("imagelist=")
                logging.info(imglist)

                self.curPageImageTotalNum = len(imglist)
                self.win_queue.put(self.iJson.generateStartJson(self.curPageUrl, self.curPageImageTotalNum))

                self.curPageFailed = 0
                self.ImageDLOKCount = 0
                imgName = 1

                for imgurl in imglist:
                    self.curImageUrl = imgurl
                    try:
                        logging.info("down %d image" % imgName)
                        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
                        timeoutCount = 0
                        percent = self.ImageDLOKCount / self.curPageImageTotalNum * 100
                        if percent > 100:
                            percent = 100
                        self.win_queue.put(self.iJson.generateDownloadJson(self.curImageUrl, self.ImageDLOKCount, percent, self.curPageFailed, "download start"))
                        while True:
                            req = urllib.request.Request(url=imgurl, headers=headers)
                            logging.info("save in:")
                            logging.info(self.saveDir)
                            with open(self.saveDir + '//'+ str(imgName)+".jpg", 'wb') as f:
                                try:
                                    res = urllib.request.urlopen(req, timeout = 10)
                                    logging.info(res)
                                    if res:
                                        data = res.read()
                                        f.write(data)
                                        self.ImageDLOKCount = self.ImageDLOKCount + 1
                                        percent = self.ImageDLOKCount / self.curPageImageTotalNum * 100
                                        if percent > 100:
                                            percent = 100
                                        self.win_queue.put(self.iJson.generateDownloadJson(self.curImageUrl, self.ImageDLOKCount, percent, self.curPageFailed, "download ok"))
                                        break
                                except Exception as e:
                                    for val in e.args:
                                        if val == 'timed out':
                                            timeoutCount = timeoutCount + 1
                                            if timeoutCount > 5:
                                                self.curPageFailed = self.curPageFailed + 1
                                                self.win_queue.put(self.iJson.generateDownloadJson(self.curImageUrl, self.ImageDLOKCount, self.curImageDLPercent, self.curPageFailed, "download error"))
                                                break
                        time.sleep(random.randint(1,3))
                    except Exception as e:
                        logging.info(imgurl+" error")
                        logging.info(e.args)
                        self.curPageFailed = self.curPageFailed + 1
                        percent = self.ImageDLOKCount / self.curPageImageTotalNum * 100
                        if percent > 100:
                            percent = 100
                        self.win_queue.put(self.iJson.generateDownloadJson(self.curImageUrl, self.ImageDLOKCount, percent, self.curPageFailed, "download error"))
                    imgName += 1
                self.win_queue.put(self.iJson.generateCompeleteJson())

if __name__ == '__main__':
    pass