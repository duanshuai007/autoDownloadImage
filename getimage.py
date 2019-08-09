#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re
import os
import time
import urllib.request
import logging
import threading
import queue
import json
import random
import chardet

import imageJson

class getimage():
    win_queue = ''
    saveDir = ''
    imageUrlHead = ''
    imageUrlBody = ''
    imageUrlTail = ''
    imageUrlType = ''
    curImageSaveDir = ''
    
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
        page = ''
        try:
            req = urllib.request.Request(url=url, headers=headers)
            #logging.info("req:")
            #logging.info(req)
            page = urllib.request.urlopen(req)
            #logging.info("urlopen")
            #logging.info(page)
        except Exception as e:
            logging.info(e.args)
            return []
        try:
            html = page.read()
            encodingtype = chardet.detect(html)
            return [encodingtype, html]
        except Exception as e:
            logging.error("getHtml error")
            logging.error(e.args)
            for val in e.args:
                if val == "timed out":
                    self.win_queue.put(self.iJson.generateErrorJson("open url timeout"))
            return []

    def start(self, html, saveimagepath):
        self.saveDir = saveimagepath.replace('\\', '//')
        urllist = html.split('/')
        self.imageUrlHead = urllist[0] + '//' + urllist[2]
        urllist = html.split('com')
        #"/manhua/147/4_309_p.html"
        url = urllist[1]
        urllist = url.split('/')
        self.imageUrlBody = urllist[1] + '/' + urllist[2]
        tailstr = urllist[3]
        tailist = tailstr.split('.')
        self.imageUrlTail = tailist[0]
        self.imageUrlType = tailist[1]
        
        logging.info(self.imageUrlHead)
        logging.info(self.imageUrlBody)
        logging.info(self.imageUrlTail)
        logging.info(self.imageUrlType)
        
        #https://www.manhuadb.com/manhua/147/4_309_p.html
        if not self.queue.full():
            self.queue.put(html)

    #因为这个网站一个页面就一张大图片，所以每次都需要打开下一个页面，获取下一个图片地址
    def getImageUrl(self, htmlstr):
        reg = r'<img class="img-fluid" src.*?="([.*\S]*?\.(?:jpg|png|jpeg|gif))" />'
        imgre = re.compile(reg)
        imgurl = re.findall(imgre, htmlstr)
        logging.info("find image url")
        logging.info(imgurl)
        if len(imgurl) == 0:
            return ''
        else:
            return imgurl[0]

    def getImageTitle(self, htmlstr):
        ret = ''
        reg = r'<title>(.*)</title>'
        imgre = re.compile(reg)
        imglist = re.findall(imgre, htmlstr)    
        res = str(imglist[0])
        logging.info("title = %s " % res)
        if len(res) > 50:
            reslist = res.split(' ')
            if len(reslist[0]) > 50:
                ret = reslist[0][0:50]
            else:
                ret = reslist[0]
        else:
            ret =  res
        ret = re.sub(r'[?*<>"|\\/:]*', '', ret)
        return ret

    def getImageType(self, url):
        typelist = url.split('.')
        num = len(typelist)
        return typelist[num - 1]

    def downloadThread(self):
        while True:
            time.sleep(1)
            if not self.queue.empty():
                self.curImageSaveDir = ''
                imgNo = 1
                imgtype = ''
                msg = self.queue.get()
                del msg
                #先读取页面，得到页面内容和编码信息
                while True:
                    if self.curImageSaveDir:
                        filename = "{}//{}.{}".format(self.curImageSaveDir, imgNo, imgtype)
                        if os.path.exists(filename) == True:
                            imgNo += 1
                            logging.info("at start: %s exists" % filename)
                            continue
                    if imgNo > 1:
                        if self.imageUrlTail.endswith('_p'):
                            imageUrl = "{}/{}/{}{}/{}".format(self.imageUrlHead, self.imageUrlBody, 
                                                    self.imageUrlTail, imgNo, self.imageUrlType)
                        else:
                            imageUrl = "{}/{}/{}_p{}/{}".format(self.imageUrlHead, self.imageUrlBody, 
                                                    self.imageUrlTail, imgNo, self.imageUrlType)
                    else:
                        imageUrl = "{}/{}/{}/{}".format(self.imageUrlHead, self.imageUrlBody, 
                                                    self.imageUrlTail, self.imageUrlType)
                    logging.info("image url : %s " % imageUrl)
                    listres = self.getHtml(imageUrl)
                    if len(listres) != 2:
                        logging.error("get html error")
                        self.win_queue.put(self.iJson.generateErrorJson("get html error"))
                        continue
                    html = listres[1]
                    encodemsg = listres[0]
                    if not html:
                        logging.error("cant open html")
                        self.win_queue.put(self.iJson.generateErrorJson("cant open html"))
                        continue
                    logging.info("the web coding: %s" % listres[0])
                    html = html.decode(encodemsg["encoding"])
                    if not self.curImageSaveDir:
                        imgGroupTitle = self.getImageTitle(html)
                        self.curImageSaveDir = self.saveDir + imgGroupTitle
                        logging.info("imagedir : %s " % self.saveDir)
                        logging.info("image save: %s" % self.curImageSaveDir)
                        try:
                            if not os.path.exists(self.curImageSaveDir):
                                os.mkdir(self.curImageSaveDir)
                        except Exception as e:
                            logging.error("image mkdir error")
                            logging.error(e.args)
                            continue
                    logging.info("get image url:")
                    self.curImageUrl = self.getImageUrl(html)
                    if not self.curImageUrl:
                        logging.error("cant find image")
                        self.win_queue.put(self.iJson.generateCompeleteJson())
                        #self.win_queue.put(self.iJson.generateErrorJson("cant find imgurl"))
                        #可能已经下载完所有图片了呢
                        break
                    logging.info(self.curImageUrl)

                    self.curImageUrl = "{}{}".format(self.imageUrlHead, self.curImageUrl)
                    imgtype = self.getImageType(self.curImageUrl)
                    try:
                        logging.info("down %d image" % imgNo)
                        self.win_queue.put(self.iJson.generateDownloadJson(self.curImageUrl, imgNo, 0, 0, "download start"))
                        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
                        timeoutCount = 0
                        filename = "{}//{}.{}".format(self.curImageSaveDir, imgNo, imgtype)
                        if os.path.exists(filename) == False:
                            while True:
                                req = urllib.request.Request(url=self.curImageUrl, headers=headers)
                                with open(filename, 'wb') as f:
                                    try:
                                        logging.info("image url request urlopen")
                                        res = urllib.request.urlopen(req, timeout = 10)
                                        if res:
                                            logging.info("image url request urlopen success, start save")
                                            data = res.read()
                                            f.write(data)
                                            logging.info("save success!!!")
                                            imgNo += 1
                                            self.win_queue.put(self.iJson.generateDownloadJson(self.curImageUrl, imgNo, 0, 0, "download ok"))
                                            break
                                        else:
                                            logging.info("image url request urlopen failed")
                                    except Exception as e:
                                        logging.error("download image error")
                                        logging.error(e.args)
                                        for val in e.args:
                                            if val == 'timed out':
                                                timeoutCount = timeoutCount + 1
                                                if timeoutCount > 5:
                                                    self.curPageFailed = self.curPageFailed + 1
                                                    self.win_queue.put(self.iJson.generateDownloadJson(self.curImageUrl, self.ImageDLOKCount, self.curImageDLPercent, self.curPageFailed, "download error"))
                                                    break
                        else:
                            logging.info("%s exists" % filename)
                            imgNo += 1
                        time.sleep(random.randint(1,3))
                    except Exception as e:
                        logging.info(self.curImageUrl + " error")
                        logging.info(e.args)

if __name__ == '__main__':
    pass