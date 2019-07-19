import sys
import logging
import queue
import threading
import time
import os
import json

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5.QtCore import QFileInfo, QBasicTimer, Qt
from PyQt5.QtGui import QColor, QFont


from imagedl import Ui_ImageDownloadtools
from getImage import getImage

class Window(QtWidgets.QMainWindow, Ui_ImageDownloadtools):
    savepath = ""
    recv_queue = queue.Queue(10)
    
    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)
        self.btn_savepath.clicked.connect(self.savePathFunc)
        self.btn_startdownload.clicked.connect(self.startDownloadFunc)
        self.btn_startdownload.setEnabled(False)
        self.textEdit.textChanged.connect(self.setDownloadButtonEnable)
        self.listWidget.clicked.connect(self.clickedListview)
                
        self.timer = QBasicTimer()
        self.timer.start(5, self)
        
        pass
        
    def savePathFunc(self):
        self.savepath = QFileDialog.getExistingDirectory(None, "select dir", "/")
        logging.info("save image to %s" % self.savepath)
        print(self.savepath)
        pass
        
    def setDownloadButtonEnable(self):
        text = self.textEdit.toPlainText()
        if not text:
            self.btn_startdownload.setEnabled(False)
        else:
            self.btn_startdownload.setEnabled(True)
        pass
    
    def clickedListview(self):
        logging.info("listWidget double click")
        pass
            
    def startDownloadFunc(self):
        textmsg = self.textEdit.toPlainText()
        if not textmsg:
            pass
        else:
            logging.info("start download, url:%s" % textmsg)
            try:
                gImage = getImage(self.recv_queue)
                gImage.start(textmsg)
            except Exception as e:
                logging.info(e.args)  
        pass
        
    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if not self.recv_queue.empty():
                msg = self.recv_queue.get()
                msgjson = json.loads(msg)
                logging.info("window recv queue:%s" % msgjson)
                if msgjson["req"] == "ready":
                    imgtotal = msgjson["total"]
                    self.label_total_num.setText(str(imgtotal))
                    pass
                elif msgjson["req"] == "download":
                    imgno = msgjson["no"]
                    imgdlper = msgjson["percent"]
                    imgdlstatus = msgjson["status"]
                    imgurl = msgjson["url"]
                    imgdlfailed = msgjson["failed"]
                    self.label_dl_num.setText(str(imgno))
                    self.progressBar.setValue(imgdlper)
                    self.label_failed_num.setText(str(imgdlfailed))
                    itemcount = self.listWidget.count()
                    if imgdlstatus == "download start":
                        item = QtWidgets.QListWidgetItem("downloading:" + imgurl)
                        self.listWidget.addItem(item)
                    elif imgdlstatus == "download error":
                        item = QtWidgets.QListWidgetItem("download failed:" + imgurl)
                        self.listWidget.takeItem(itemcount)
                        self.listWidget.addItem(item)
                        self.listWidget.item(itemcount).setBackground(QColor("red"))
                    elif imgdlstatus == "download ok":
                        item = QtWidgets.QListWidgetItem("download ok:" + imgurl)
                        self.listWidget.takeItem(itemcount)
                        self.listWidget.addItem(item)
                        self.listWidget.item(itemcount).setBackground(QColor("gray"))
                    pass
                elif msgjson["req"] == "compelete":
                    self.progressBar.setValue(0)
                    pass
                elif msgjson["req"] == "error":
                    pass


if __name__ == "__main__":
    logging.basicConfig(filename="mydebug.log", level=logging.DEBUG,format='%(asctime)s %(levelname)s:%(filename)s[line:%(lineno)d]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

    