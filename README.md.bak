在生成exe文件时，生成过程没有问题。但是执行exe文件时提示找不到getimage模块
最终解决办法是发现getimage.py内的代码段缩紧的问题。
不是普通的缩紧错误，因为在命令行下执行python testqt.py是可以正常执行没有问题的。
后来发现在行与行之间,例如这段代码

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

在第10行和第23行，用光标移动过去，或者是复制到sublime中查看，看到该行是完全的空白，这样才行。
具体是不是这个问题所导致的我也不能完全肯定。但是我把所有行的缩进都改了以后就好使了