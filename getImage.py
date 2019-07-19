#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import re
import sys
import os
import time
import socket
import urllib.request
import logging
import threading
import queue
from urllib.request import urlretrieve
import json

from imageJson import imageJson

class getImage():
    win_queue = ''
    curPageUrl = ''
    curPageImageTotalNum = 0
    curImageUrl = ''
    curImageNo = 0
    curImageDLPercent = 0
    curPageFailed = 0
    
    def __init__(self, window_queue):
        self.queue = queue.Queue(5)
        self.win_queue = window_queue
        self.iJson = imageJson()
        thread = threading.Thread(target=self.downloadThread, args=[])
        thread.setDaemon(True)
        thread.start()
        pass
        
    def getHtml(self, url):
        logging.info("gethtml:%s" % url)
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        req = urllib.request.Request(url=url, headers=headers)
        page = urllib.request.urlopen(req)
        html = page.read()
        return html
    
    def start(self, html):
        #logging.info("start!")
        if not self.queue.full():
            self.queue.put(html)
        
    def getImageList(self, htmlstr):
        #logging.info("get image list")
        reg = r'src ="([.*\S]*\.jpg)"'
        imgre = re.compile(reg)
        imglist = re.findall(imgre, htmlstr)
        return imglist
        pass
        
    def callback(self, blocknum, blocksize, totalsize):
        percent = (blocknum * blocksize / totalsize) * 100
        status = ""
        if percent >= 100:
            percent = 100
            status = "download ok"
       	else:
       			status = "downloading"     
        self.curImageDLPercent = percent
        #self.win_queue.put("download percent %d" % percent)
        logging.info("download:%d" % percent)
        self.win_queue.put(self.iJson.generateDownloadJson(self.curImageUrl, self.curImageNo, self.curImageDLPercent, self.curPageFailed, status))
        
    def downloadThread(self):
        
        while True:
            time.sleep(0.5)
            if not self.queue.empty():
                msg = self.queue.get()
                self.curPageUrl = msg
                html = self.getHtml(msg)
                if not html:
                    self.win_queue.put(self.iJson.genarateErrorJson("cant open html"))
                    continue
                html = html.decode('UTF-8')
                
                imgName = 1
                totalfailed = 0
                imglist = self.getImageList(html)
                if not imglist:
                    self.win_queue.put(self.iJson.genarateErrorJson("cant find imgurl"))
                    continue
                logging.info("imagelist=")
                logging.info(imglist)
                
                self.curPageImageTotalNum = len(imglist)
                self.win_queue.put(self.iJson.generateStartJson(self.curPageUrl, self.curPageImageTotalNum))
                
                self.curPageFailed = 0
                
                for imgurl in imglist:
                    
                    self.curImageUrl = imgurl
                    self.curImageNo = imgName
                    self.curImageDLPercent = 0

                    try:
                        logging.info("down %d image" % imgName)
                        self.win_queue.put(self.iJson.generateDownloadJson(self.curImageUrl, self.curImageNo, self.curImageDLPercent, self.curPageFailed, "download start"))
                       
                        #f = open('C://Users//Administrator//git//autoDownloadImage//'+ str(imgName)+".jpg", 'wb')
                        #headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
                        #req = urllib.request.Request(url=imgurl, headers=headers)
                        #f.write((urllib.request.urlopen(req)).read())
                        #f.close()
                        
                        urlretrieve(imgurl, 'C://Users//Administrator//git//autoDownloadImage//'+ str(imgName)+".jpg", self.callback)
                        logging.info(imgurl)
                        
                    except Exception as e:
                        logging.info(imgurl+" error")
                        logging.info(e.args)
                        self.curPageFailed = self.curPageFailed + 1
                        self.win_queue.put(self.iJson.generateDownloadJson(self.curImageUrl, self.curImageNo, self.curImageDLPercent, self.curPageFailed, "download error"))
                    imgName += 1
                
                self.win_queue.put(self.iJson.generateCompeleteJson())