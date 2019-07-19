from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5.QtCore import QFileInfo
 
 
class MyWindow(QWidget):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.myButton = QtWidgets.QPushButton(self)
        self.myButton.setObjectName("btn")
        self.myButton.setText('123')
        self.myButton.clicked.connect(self.msg)
 
 
    def msg(self):
 
        directory1 = QFileDialog.getExistingDirectory(self, "select", "/")
        print(directory1)
 
        fileName, filetype = QFileDialog.getOpenFileName(self, "select file", "/", "All Files (*);;Text Files (*.txt)")
        print(fileName, filetype)
        print(fileName)
        fileinfo = QFileInfo(fileName)
        print(fileinfo)
        file_name = fileinfo.fileName()
        print(file_name)
        file_suffix = fileinfo.suffix()
        print(file_suffix)
        file_path = fileinfo.absolutePath()
        print(file_path)
 
        files, ok1 = QFileDialog.getOpenFileNames(self, "duo file select", "/", "all (*);;text (*.txt)")
        print(files, ok1)
 
        fileName2, ok2 = QFileDialog.getSaveFileName(self, "file save", "/", "image file (*.png);;(*.jpeg)")
        print(fileName2)
 
 
if __name__ == "__main__":
    import sys
 
    app = QtWidgets.QApplication(sys.argv)
    myshow = MyWindow()
    myshow.show()
    sys.exit(app.exec_())