#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys
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
from logger import LoggingConsumer, LoggingProducer

class Window(QtWidgets.QMainWindow, Ui_ImageDownloadtools):
    rootdir = ""
    recv_queue = None
    gImage = None
    download_flag = False
    DEFAULT_SAVE_DIR='C://Users//Administrator//autoDownloadImage//'
    wait_download_list = []
    cur_download_url = None
    
    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.btn_savepath.clicked.connect(self.savePathFunc)
        self.btn_startdownload.clicked.connect(self.startDownloadFunc)
        self.btn_startdownload.setEnabled(False)
        self.btn_opensavepath.clicked.connect(self.openSaveImagePath)
        self.btn_opensavepath.setEnabled(False)
        self.textEdit.textChanged.connect(self.setDownloadButtonEnable)
        self.listWidget_downloadinfo.clicked.connect(self.clickedListWidget)
        self.listWidget_wiatdownload.clicked.connect(self.clickedListWidget)
        self.logger = LoggingProducer().get_default_logger()
        self.timer = QBasicTimer()
        self.timer.start(1, self)
        self.recv_queue = queue.Queue(10)
        self.gImage = getimage.getimage(self.recv_queue)

    '''选择图片保存的目录'''
    def savePathFunc(self):
        self.rootdir = QFileDialog.getExistingDirectory(None, "选择图片保存目录", "/")
        self.logger.info("保存文件到:{}".format(self.rootdir))
        self.label_curdlpath.setText(self.rootdir)
        self.btn_opensavepath.setEnabled(True)

    '''打开图片保存的文件夹'''
    def openSaveImagePath(self):
        if not os.path.exists(self.rootdir):
            self.logger.info("path:{} not exists".format(self.rootdir))
            return
        if sys.platform == 'win32':
            os.startfile(self.rootdir)
        else:
            cmd = "open %s".format(self.rootdir)
            os.system(cmd)

    '''下载按钮使能禁止'''
    def setDownloadButtonEnable(self):
        text = self.textEdit.toPlainText()
        if not text:
            self.btn_startdownload.setEnabled(False)
        else:
            self.btn_startdownload.setEnabled(True)
        pass

    def clickedListWidget(self):
        self.logger.info("ListWidget click")

    '''启动下载'''
    def startDownloadFunc(self):
        textmsg = self.textEdit.toPlainText()
        '''链接等于上一次的链接，并且不为空'''
        if textmsg:
            if self.download_flag is True:
                if textmsg not in self.wait_download_list and textmsg != self.cur_download_url:
                    self.wait_download_list.append(textmsg)
                    msg = {
                        'req' : 'waitdownload',
                        'url' : textmsg,
                    }
                    self.recv_queue.put(json.dumps(msg))
                self.logger.info(self.wait_download_list)
                QMessageBox.warning(self, "Warning", "已将该链接加入到下载等待队列", QMessageBox.Ok)
                return

            ''' 图片保存目录的生成，以self.savepath作为根目录，在该目录内创建文件夹，文件夹以年月日时分秒明明
            更新:该目录作为图片保存的根目录，以图片链接内地title作为文件夹名
            '''
            tmp_save_dir = self.rootdir
            if not tmp_save_dir:
                '''没有设置默认目录'''
                if not os.path.exists('D://'):
                    if not os.path.exists(self.DEFAULT_SAVE_DIR):
                        os.mkdir(self.DEFAULT_SAVE_DIR)
                    tmp_save_dir = self.DEFAULT_SAVE_DIR
                else:
                    if not os.path.exists('D://autoDownloadImage'):
                        os.mkdir('D://autoDownloadImage')
                    tmp_save_dir = 'D://autoDownloadImage'
                self.rootdir = tmp_save_dir
            self.logger.info("save image root dir:{}".format(tmp_save_dir))
            tmp_save_dir = tmp_save_dir.replace('//','\\')
            tmp_save_dir = tmp_save_dir.replace('/', '\\')
			
            self.label_curdlpath.setText(tmp_save_dir)
            self.listWidget_downloadinfo.clear()
            self.label_total_num.setText("0")
            self.label_dl_num.setText("0")
            self.label_failed_num.setText("0")
            self.progressBar.setValue(0)
			
            self.logger.info("start download, url:{}".format(textmsg))
            try:
                self.btn_opensavepath.setEnabled(True)
                self.gImage.start(textmsg, tmp_save_dir)
                self.download_flag = True
                self.cur_download_url = textmsg
            except Exception as e:
                self.logger.error("startDownloadFunc error:{}".format(e.args))  

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if not self.recv_queue.empty():
                msg = self.recv_queue.get()
                msgjson = json.loads(msg)
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

                    itemcount = self.listWidget_downloadinfo.count()
                    #logging.info("item count = %d" % itemcount)
                    if imgdlstatus == "download start":
                        item = QtWidgets.QListWidgetItem("downloading:" + imgurl)
                        self.listWidget_downloadinfo.addItem(item)
                    elif imgdlstatus == "download error":
                        if itemcount >= 1:
                            item = QtWidgets.QListWidgetItem("download failed:" + imgurl)
                            self.listWidget_downloadinfo.takeItem(itemcount - 1)
                            self.listWidget_downloadinfo.addItem(item)
                            self.listWidget_downloadinfo.item(itemcount - 1).setBackground(QColor("red"))
                    elif imgdlstatus == "download ok":
                        if itemcount >= 1:
                            item = QtWidgets.QListWidgetItem("download ok:" + imgurl)
                            self.listWidget_downloadinfo.takeItem(itemcount - 1)
                            self.listWidget_downloadinfo.addItem(item)
                            self.listWidget_downloadinfo.item(itemcount - 1).setBackground(QColor("gray"))
                        if imgdlper == 100:
                            self.progressBar.setValue(0)
                            self.label_dl_num.setText("Download finish")
                            if len(self.wait_download_list) != 0:
                                url = self.wait_download_list.pop(0)
                                self.logger.info("url:{} list:{}".format(url, self.wait_download_list))
                                self.gImage.start(url, self.rootdir)
                                self.cur_download_url = url
                                self.listWidget_wiatdownload.takeItem(0)
                            else:
                                self.download_flag = False
                elif msgjson["req"] == "compelete":
                    self.progressBar.setValue(0)
                    self.label_dl_num.setText("Download finish")
                    if len(self.wait_download_list) != 0:
                        url = self.wait_download_list.pop(0)
                        self.logger.info("url:{} list:{}".format(url, self.wait_download_list))
                        self.gImage.start(url, self.rootdir)
                        self.cur_download_url = url
                        self.listWidget_wiatdownload.takeItem(0)
                    else:
                        self.download_flag = False
                elif msgjson["req"] == "waitdownload":
                    item = QtWidgets.QListWidgetItem(msgjson['url'])
                    self.listWidget_wiatdownload.addItem(item)
                elif msgjson["req"] == "error":
                    self.logger.error("connect error,retry download")
                    self.gImage.start(self.cur_download_url, self.rootdir)
                    pass

if __name__ == "__main__":
    LoggingConsumer()
    '''
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s:%(filename)s[line:%(lineno)d]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    #logging.basicConfig(filename="mydebug.log", level=logging.DEBUG,format='%(asctime)s %(levelname)s:%(filename)s[line:%(lineno)d]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    '''
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())