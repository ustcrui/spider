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
    name = selector.xpath('//div[@class="ys-head"]//h1')
    list = []
    for info in name:
        list.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    return ''.join(list)

'''获取基本信息'''
def basic_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    basic = selector.xpath('//div[@class="intro"]/p')
    info_box = []
    for info in basic:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    basic = ' '.join(info_box)
    return basic

'''获取属性信息'''
def attribute_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    basicinfo = selector.xpath('//div[@class="ys-brief"]/ul//span[not(@class)]')
    info_box = []
    data = {}
    for info in basicinfo:
        info = info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
        info = info.split("：")
        data[info[0]] = info[1]
    analyse = selector.xpath('//div[@class="ys-brief"]//div[@id="ys-img"]//@data-data')
    if analyse != None:
        info_box = []
        for info in analyse:
            info_box.append(info.replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','').replace('<br>',''))
        analyse_info = ' '.join(info_box)
        data['分析结果'] = analyse_info
    return data

'''其他一些信息'''
def other_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    data['正常值'] = ' '.join(selector.xpath('//div[@class="ys-normal"]/p/text()'))
    data['临床意义'] = ' '.join(selector.xpath('//div[@class="ys-clinical" and @name="3F"]/p/text()')).replace('\r','').replace('\t','').replace('\n','').replace(' ','')
    data['注意事项'] = ' '.join(selector.xpath('//div[@class="ys-clinical" and @name="4F"]/p/text()')).replace('\r','').replace('\t','').replace('\n','').replace(' ','')
    data['检查过程'] = ' '.join(selector.xpath('//div[@class="ys-clinical" and @name="5F"]/p/text()')).replace('\r','').replace('\t','').replace('\n','').replace(' ','')
    data['不适宜人群'] = ' '.join(selector.xpath('//div[@class="ys-clinical" and @name="6F"]/p/text()')).replace('\r','').replace('\t','').replace('\n','').replace(' ','')
    data['不良反应与风险'] = ' '.join(selector.xpath('//div[@class="ys-clinical" and @name="7F"]/p/text()')).replace('\r','').replace('\t','').replace('\n','').replace(' ','')
    return data

'''相关疾病'''
def related_disease(url):
    html = get_html(url)
    selector = etree.HTML(html)
    re_list = []
    title = selector.xpath('//div[@class="w_cr1"]//a/text()')
    href = selector.xpath('//div[@class="w_cr1"]//@href')
    for i in range(len(title)):
        data = {}
        data[title[i]] = href[i]
        re_list.append(data)
    return re_list

def main(url):
    start = time.time()
    data = {}
    data['类型'] = "检查"
    data['网址'] = url
    data['名称'] = name_info(url)
    data['简介'] = basic_info(url)
    data['属性'] = attribute_info(url)
    data = {**data,**other_info(url)}
    data['相关疾病'] = related_disease(url)
    end = time.time()
    take_time = end - start
    print('%s已爬取完成,用时%f秒' % (data['名称'], take_time))
    return data

'''获取所有检查链接'''
main_html = get_html('http://tag.120ask.com/jiancha')
main_selector = etree.HTML(main_html)
main_list = main_selector.xpath('//div[@class="w_conr1 clears"]//p[@class="clears"]//@href')
urls = []
for url in main_list:
    url = 'http://tag.120ask.com' + url
    html = get_html(url)
    selector = etree.HTML(html)
    href = selector.xpath('//div[@class="w_conr"]//li//@href')
    for hr in href:
        urls.append('http://tag.120ask.com' + hr)

#test_url = []
#for i in range(10):
#   test_url.append(urls[i])

if __name__ == '__main__':
    start_time = time.time()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    check = pool.map(main,urls)
    with open('check.json','w',encoding='utf-8') as f:
        json_str = json.dumps(check,ensure_ascii=False)
        f.write(json_str)
    pool.close()
    pool.join()
    end_time = time.time()
    print(end_time-start_time)