import requests

s=requests.session()

headers={
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.9',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Host':'www.jj20.com',
'If-Modified-Since':'Fri, 21 Dec 2018 03:58:29 GMT',
'If-None-Match':'"cf51d66ee198d41:0"',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.15 Safari/537.36',
}

s.headers.update(headers)
url=r'http://p8.urlpic.club/pic20190701/upload/image/20190719/71906356228.jpg'
html=s.get(url=url)
print(html)

with open('test01.jpg', 'wb') as file:
    file.write(html.content)