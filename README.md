##Download Image Tools

> 1.生成exe文件执行时发现找不到getimage模块  
>> 在生成exe文件时，生成过程没有问题。但是执行exe文件时提示找不到getimage模块  
>> 最终解决办法是发现getimage.py内的代码段缩紧的问题。  
>> 不是普通的缩紧错误，因为在命令行下执行python testqt.py是可以正常执行没有问题的。  
>> 后来发现在行与行之间,例如这段代码  

```
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
```

>> 在第10行和第23行，用光标移动过去，或者是复制到sublime中查看，看到该行是完全的空白，这样才行。  
>> 具体是不是这个问题所导致的我也不能完全肯定。但是我把所有行的缩进都改了以后就好使了  
>> 在测试中发现如果有用#号注释的语句也会导致出现找不到getimage模块的错误  
>> 如果用'''something'''来注释也是一样的现象  

> 发现如果注释语句用中文则会出现错误，但是如果用英文就没有问题。

## 安装 python qt5 工具

```
pip install PyQt5-tools -i https://pypi.douban.com/simple
```

## 打开qt designer工具

```
pyqt5-tools.exe designer
```

## 通过ui文件生成py文件
```
pyuic.exe ***.ui -o ***.py
```

## 生成exe文件方法
```
安装pyinstaller工具
pip install pyinstaller
然后将pyinstaller工具添加到环境变量(WIN7)
$ which python
/c/Users/Administrator/AppData/Local/Programs/Python/Python37/python
一般pyinstaller就在/c/Users/Administrator/AppData/Local/Programs/Python/Python37/python/Scripts目录中
打开"计算机->属性->高级系统设置->环境变量"，在系统变量中寻找PATH，将/c/Users/Administrator/AppData/Local/Programs/Python/Python37/python/Scripts添加到PATH的尾部。


在项目根目录下执行
pyinstaller -F testqt.py
会在根目录的dist目录下生成testqt.exe文件
如果不想要显示控制台
pyinstaller -Fw testqt.py
```
