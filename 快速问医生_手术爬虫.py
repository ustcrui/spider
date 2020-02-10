import requests
import re
import multiprocessing
import os
import time
import json
from lxml import etree
from urllib import parse

def get_html(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
    }
    proxies = {
        'http':None,
        'https':None
    }            #禁用代理
    html = requests.get(url=url , headers= headers, proxies=proxies)
    html.encoding = 'utf-8'
    return html.text

def name_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    name = selector.xpath('//div[@class="w_nav m980"]//h3/text()')
    return ''.join(name)

def basic_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    basic = selector.xpath('//div[@class="w_c1"]//dd[@class="w_d3"]')
    info_box = []
    for info in basic:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    return ' '.join(info_box)

def attribute_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data={}
    total_info = selector.xpath('//div[@class="w_c1"]//dd[not(@id)]//span')
    for info in total_info:
        info = info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
        info = info.split("：")
        data[info[0]] = info[1]
    return data

'''辅助查找相关信息'''
def related_tool(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data = selector.xpath('//div[@class="w_contl fl"]')
    info_box = []
    for info in data:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    return ' '.join(info_box)

'''相关信息'''
def related_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    title = selector.xpath('//div[@class="w_nav m980"]//div[@class="w_na clears"]//a[not(@class)]/text()')
    href = selector.xpath('//div[@class="w_nav m980"]//div[@class="w_na clears"]//a[not(@class)]//@href')
    for i in range(len(title)):
        data[title[i]] = related_tool('http://tag.120ask.com/' + href[i])
    return data

def main(url):
    start = time.time()
    data = {}
    data['类型'] = "手术"
    data['网址'] = url
    data['名称'] = name_info(url)
    data['简介'] = basic_info(url)
    data['属性'] = attribute_info(url)
    data['手术相关'] = related_info(url)
    end = time.time()
    take_time = end - start
    print('%s已爬取完成,用时%f秒' % (data['名称'], take_time))
    return data

'''获取所有手术相关链接'''
html = get_html('http://tag.120ask.com/shoushu/pinyin.html')
selector = etree.HTML(html)
total_list = selector.xpath('//div[@class="w_sx m980"]//li//@href')
urls = []
for info in total_list:
    urls.append('http://tag.120ask.com' + info)

if __name__ == '__main__':
    start_time = time.time()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    operation = pool.map(main,urls)
    with open('operation.json','w',encoding='utf-8') as f:
        json_str = json.dumps(operation,ensure_ascii=False)
        f.write(json_str)
    pool.close()
    pool.join()
    end_time = time.time()
    print(end_time-start_time)