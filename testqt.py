#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import logging
import queue
import threading
import time
import os
import json

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox
from PyQt5.QtCore import QFileInfo, QBasicTimer
from PyQt5.QtGui import QColor

import getimage
from imagedl import Ui_ImageDownloadtools

class Window(QtWidgets.QMainWindow, Ui_ImageDownloadtools):
    savepath = ""
    recv_queue = ''
    gImage = ''
    DEFAULT_SAVE_DIR='C://Users//Administrator//autoDownloadImage//'
    '''
    上一次的下载链接，用来防止连续点击
    '''
    last_dl_url= ""
    cur_save_path = ""
        
    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.btn_savepath.clicked.connect(self.savePathFunc)
        self.btn_startdownload.clicked.connect(self.startDownloadFunc)
        self.btn_startdownload.setEnabled(False)
        self.btn_opensavepath.clicked.connect(self.openSaveImagePath)
        self.btn_opensavepath.setEnabled(False)
        self.textEdit.textChanged.connect(self.setDownloadButtonEnable)
        self.listWidget.clicked.connect(self.clickedListWidget)
                
        self.timer = QBasicTimer()
        self.timer.start(5, self)
        self.recv_queue = queue.Queue(10)
        self.gImage = getimage.getimage(self.recv_queue)
        pass

    '''选择图片保存的目录'''
    def savePathFunc(self):
        self.savepath = QFileDialog.getExistingDirectory(None, "选择图片保存目录", "/")
        logging.info("save image to %s" % self.savepath)
        self.label_curdlpath.setText(self.savepath)
        self.btn_opensavepath.setEnabled(True)
        print(self.savepath)
        pass
        
    '''打开图片保存的文件夹'''
    def openSaveImagePath(self):
        try:
            cmd = "start explorer %s" % self.cur_save_path
            os.system(cmd)
        except Exception as e:
            logging.error("open image lpath[%s] failed" % self.savepath)
            logging.error(e.args)
        pass

    '''下载按钮使能禁止'''
    def setDownloadButtonEnable(self):
        text = self.textEdit.toPlainText()
        if not text:
            self.btn_startdownload.setEnabled(False)
        else:
            self.btn_startdownload.setEnabled(True)
        pass
    
    def clickedListWidget(self):
        logging.info("ListWidget click")
        pass
            
    '''启动下载'''
    def startDownloadFunc(self):
        textmsg = self.textEdit.toPlainText()
        '''链接等于上一次的链接，并且不为空'''
        if textmsg:
            if textmsg == self.last_dl_url:
                QMessageBox.warning(self,"Warning","下载已经开始，不需要多次点击",QMessageBox.Ok)
                return

            '''
            图片保存目录的生成，以self.savepath作为根目录，在该目录内创建文件夹，文件夹以年月日时分秒明明
            '''
            saveDir = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            if self.savepath:
                '''如果设置了默认的根目录'''
                saveDir = self.savepath + '//' + saveDir
                if not os.path.exists(saveDir):
                    os.mkdir(saveDir)
                pass
            else:
                if not os.path.exists('D://'):
                    if not os.path.exists(self.DEFAULT_SAVE_DIR):
                        os.mkdir(self.DEFAULT_SAVE_DIR)
                    saveDir = self.DEFAULT_SAVE_DIR + saveDir
                else:
                    saveDir = 'D://autoDownloadImage//' + saveDir
                '''没有设置默认目录'''
                pass

            if not os.path.exists(saveDir):
                os.mkdir(saveDir)
                           
            saveDir = saveDir.replace('//','\\')
            self.cur_save_path = saveDir.replace('/', '\\')
            
            self.last_dl_url = textmsg

            self.label_curdlpath.setText(self.cur_save_path)
            self.listWidget.clear()
            self.label_total_num.setText("0")
            self.label_dl_num.setText("0")
            self.label_failed_num.setText("0")
            self.progressBar.setValue(0)

            logging.info("start download, url:%s" % textmsg)
            try:
                self.btn_opensavepath.setEnabled(True)
                self.gImage.start(textmsg, saveDir)
            except Exception as e:
                logging.info(e.args)  
        pass
        
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if not self.recv_queue.empty():
                msg = self.recv_queue.get()
                msgjson = json.loads(msg)
                #logging.info("window recv queue:%s" % msgjson)
                if msgjson["req"] == "ready":
                    imgtotal = msgjson["total"]
                    self.label_total_num.setText(str(imgtotal))
                    pass
                elif msgjson["req"] == "download":
                    imgcount = msgjson["count"]
                    imgdlper = msgjson["percent"]
                    imgdlstatus = msgjson["status"]
                    imgurl = msgjson["url"]
                    imgdlfailed = msgjson["failed"]
                    self.label_dl_num.setText(str(imgcount))
                    self.progressBar.setValue(imgdlper)
                    self.label_failed_num.setText(str(imgdlfailed))
                    
                    itemcount = self.listWidget.count()
                    #logging.info("item count = %d" % itemcount)
                    if imgdlstatus == "download start":
                        item = QtWidgets.QListWidgetItem("downloading:" + imgurl)
                        self.listWidget.addItem(item)
                    elif imgdlstatus == "download error":
                        if itemcount >= 1:
                            item = QtWidgets.QListWidgetItem("download failed:" + imgurl)
                            self.listWidget.takeItem(itemcount - 1)
                            self.listWidget.addItem(item)
                            self.listWidget.item(itemcount - 1).setBackground(QColor("red"))
                    elif imgdlstatus == "download ok":
                        if itemcount >= 1:
                            item = QtWidgets.QListWidgetItem("download ok:" + imgurl)
                            self.listWidget.takeItem(itemcount - 1)
                            self.listWidget.addItem(item)
                            self.listWidget.item(itemcount - 1).setBackground(QColor("gray"))
                    pass
                elif msgjson["req"] == "compelete":
                    self.progressBar.setValue(0)
                    pass
                elif msgjson["req"] == "error":
                    pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s:%(filename)s[line:%(lineno)d]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    #logging.basicConfig(filename="mydebug.log", level=logging.DEBUG,format='%(asctime)s %(levelname)s:%(filename)s[line:%(lineno)d]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

