#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import requests
# ͼƬ��ַ
url = 'http://p8.urlpic.club/pic20190701/upload/image/20190719/71906356228.jpg'
html = requests.get(url)
print(html)
# ��ͼƬ���浽D��
with open("C:/1.jpg","wb")as f:
    f.write(html.content)