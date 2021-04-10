#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import requests
from lxml import etree
import time
from selenium import webdriver
import os

PICTURES_PATH = os.path.join(os.getcwd(), './pictures/')
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/65.0.3325.181 Safari/537.36',
    'Referer': "http://www.mmjpg.com"
}

class Spider(object):
    def __init__(self):
        self.page_num = 40
        #self.page_urls = ['http://www.mmjpg.com/']
        self.girl_urls = []
        self.girl_name = ''
        self.pic_urls = []


    def get_girl_urls(self):
        html = requests.get("http://p8.urlpic.club/pic20190701/upload/image/20190719/71906356228.jpg").content
        print(html)
        selector = etree.HTML(html)
        print(selector)
        self.girl_urls = (selector.xpath('//span[@class="title"]/a/@href'))
        print(self.girl_urls)
        driver = webdriver.Chrome()

        for girl_url in self.girl_urls:
            driver.get(girl_url)
            time.sleep(3)
            driver.find_element_by_xpath('//em[@class="ch all"]').click()
            time.sleep(3)
            # 这里暂停3秒之后获取html的源代码
            html = driver.page_source
            selector = etree.HTML(html)
            self.girl_name = selector.xpath('//div[@class="article"]/h2/text()')[0]
            self.pic_urls = selector.xpath('//div[@id="content"]/img/@data-img')
            try:
                self.download_pic()
            except Exception as e:
                print("{}save failed".format(self.girl_name) + str(e))

    def download_pic(self):
        try:
            os.mkdir(PICTURES_PATH)
        except:
            pass
        girl_path = PICTURES_PATH + self.girl_name
        try:
            os.mkdir(girl_path)
        except Exception as e:
            print("{}file already exist".format(self.girl_name))
        img_name = 0
        for pic_url in self.pic_urls:
            img_name += 1
            img_data = requests.get(pic_url,headers =headers)
            pic_path = girl_path + '/' + str(img_name)+'.jpg'
            if os.path.isfile(pic_path):
                print("{}{}already exist".format(self.girl_name, img_name))
                pass
            else:
                with open(pic_path, 'wb')as f:
                    f.write(img_data.content)
                    print("saveing{}{}".format(self.girl_name, img_name))
                    f.close()
        return

def main():
    spider = Spider()
    spider.get_girl_urls()

if __name__ == '__main__':
    main()