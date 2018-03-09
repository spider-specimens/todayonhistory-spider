# -*- coding: UTF-8 -*-
import time
import requests
import numpy as np
from bs4 import BeautifulSoup
import functools
import re
from urllib.parse import urlparse, parse_qs
import psycopg2

headers=[
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}
]

class Spider(object):
    
    pageSize = 40

    def __init__(self):
        self.db = psycopg2.connect(database="tih", user="postgres", password="123456", host="127.0.0.1", port="5432")
        print("connect db success.")

    def fetchListData(self, month, day, page = 0):
        htmlURL = "http://www.todayonhistory.com/" + str(month) + '/' + str(day)
        apiURL = "http://www.todayonhistory.com/index.php?m=content&c=index&a=json_event&page=" + str(page) + "&pagesize=" + str(self.pageSize) + "&month=" + str(month) + "&day=" + str(day)

        res = requests.get(
            htmlURL if page == 0 else apiURL,
            headers=headers[np.random.randint(0, len(headers))]
        )

        result = []

        if page == 0:
            soup = BeautifulSoup(res.text, "html5lib").find(id="container").find_all("li")

            for item in soup:
                
                _data = {}
                txtLink = item.select('.text > a, a.txt')
                img = item.find('img')
                year = item.select('.time .moh b')

                if not len(txtLink):
                    continue

                txtLink = txtLink[0]
                description = item.select('.text > p')

                result.append({
                    'url': txtLink.get('href'),
                    'title': txtLink.text,
                    'thumb': img.get('data-original') if img else '',
                    'solaryear': year[0].text if len(year) else '',
                    'description': description[0].text if len(description) else '',
                })
        else:
            for item in res.json():
                result.append({
                    'url': item['url'],
                    'title': item['title'],
                    'thumb': item['thumb'],
                    'solaryear': item['solaryear'],
                    'description': item['description'],
                })

        return result
    
    def fetchAllListData(self, month, day):
        page = 0
        result = []

        while (1):
            _result = self.fetchListData(month, day, page)

            result = result + _result
            
            if (len(_result) == 0 or len(_result) < self.pageSize):
                break
            
            page = page + 1

        return result
            
    def fetchDetailData(self, url):
        res = requests.get(url, headers=headers[np.random.randint(0, len(headers))])

        res.encoding = 'utf-8'

        if (res.status_code >= 400):
            print(err)

        soup = BeautifulSoup(res.text, "html5lib")

        body = soup.select('.body')
        idElm = soup.select('script[src^="http://www.todayonhistory.com/api.php"]')

        return {
            "body": body[0].prettify() if len(body) else '',
            'id': parse_qs(urlparse(idElm[0].get('src')).query)['id'][0] if idElm else '',
        }

    def fetchDayAllData(self, month, day):
        _list = self.fetchAllListData(month, day)
        print('已获取%d月%d日全部列表数据，共计%d条，开始获取详情数据。' % (month, day, len(_list)))

        for index, item in enumerate(_list):
            time.sleep(np.random.rand() * 3)
            print('开始获取第%d条数据：%s页面。' % (index + 1, item['url']))
            
            _detail = self.fetchDetailData(item['url'])

            item['id'] = _detail['id']
            item['body'] = _detail['body']
            item['month'] = month
            item['day'] = day

            print('已获取第%d条数据：第三方id为%s。' % (index + 1, item['id']))

            self.saveData(item)
        
        print('已获取%d月%d日全部数据。' % (month, day))

        return _list

    def saveData(self, data):
        cur = self.db.cursor()

        now = int(time.time())

        cur.execute("insert into events (title, description, body, month, day, target, target_id, target_detail_url, create_time, update_time, status) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (data['title'], data['description'], data['body'], data['month'], data['day'], 'www.todayinhistory.com', data['id'], data['url'], now, now, 1))

        self.db.commit()
        print("数据已保存。")

    def getAllData(self):
        for month in range(1, 12):
            maxDay = 30
            if (month in [1, 3, 5, 7, 8, 10, 12]):
                maxDay = 31
            if (month in [2]):
                maxDay = 29
            
            for day in range(1, maxDay):
                self.fetchDayAllData(month, day)

        print('已获取全部数据。')

if __name__ == "__main__":
    spider = Spider()
    spider.getAllData()