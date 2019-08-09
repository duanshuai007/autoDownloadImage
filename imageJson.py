#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json
#http://blog.sina.com.cn/s/blog_ae6c02970102whng.html

class imageJson():
    REQ_START = {
        "req":"ready",
        "total":0,
        "url":'',
    }
    
    REQ_DOWNLOAD = {
        "req":"download",
        "no":0,
        "url":"",
        "percent":0,
        "failed":0,
        "status":"",
    }
    
    REQ_COMPELETE = {
        "req":"compelete",
    }

    REQ_ERROR = {
        "req":"error",
        "status":""
    }

    def __init__(self):
        pass

    def generateStartJson(self, url, num):
        self.REQ_START["total"] = num
        self.REQ_START["url"] = url
        return json.dumps(self.REQ_START)

    def generateDownloadJson(self, url, num, percent, failednum, status):
        self.REQ_DOWNLOAD["url"] = url
        self.REQ_DOWNLOAD["count"] = num
        self.REQ_DOWNLOAD["percent"] = percent
        self.REQ_DOWNLOAD["status"] = status
        self.REQ_DOWNLOAD["failed"] = failednum
        return json.dumps(self.REQ_DOWNLOAD)

    def generateCompeleteJson(self):
        return json.dumps(self.REQ_COMPELETE)

    def generateErrorJson(self, msg):
        self.REQ_ERROR["status"] = msg
        return json.dumps(self.REQ_ERROR)

if __name__ == '__main__':
    pass