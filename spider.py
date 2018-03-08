# -*- coding: UTF-8 -*-
import time
import requests
import numpy as np
from bs4 import BeautifulSoup
import functools
import re
from urllib.parse import urlparse, parse_qs

headers=[
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}
]

class Spider(object):
    
    pageSize = 40

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
            "body": body[0] if len(body) else '',
            'id': parse_qs(urlparse(idElm[0].get('src')).query)['id'][0] if idElm else '',
        }

    def fetchDayAllData(self, month, day):
        _list = self.fetchAllListData(month, day)
        print('已获取{month}月{day}日全部列表数据，共计{length}条，开始获取详情数据。'.format(month=month, day=day, length=len(_list)))

        for index, item in enumerate(_list):
            time.sleep(np.random.rand() * 3)
            print('开始获取第{index}条数据：{url}页面。'.format(index=index + 1, url=item['url']))
            
            _detail = self.fetchDetailData(item['url'])

            item['id'] = _detail['id']
            item['body'] = _detail['body']
            print('已获取第{index}条数据：第三方id为{_id}。'.format(index=index + 1, _id=item['id']))
        
        print('已获取{month}月{day}日全部数据。')

        return _list

if __name__ == "__main__":
    spider = Spider()

    # result = spider.fetchAllListData(3, 8)
    # print(len(result))

    result = spider.fetchDayAllData(3, 8)

    print(result)