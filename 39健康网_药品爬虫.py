import requests
import re
import multiprocessing
import os
import time
import json
from lxml import etree
from urllib import parse
from selenium import webdriver

def get_html(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
    }
    proxies = {
        'http':None,
        'https':None
    }            #禁用代理
    i = 0
    while i < 3:
        try:
            html = requests.get(url=url, headers=headers, proxies=proxies, timeout=5)
            html.encoding = 'utf-8'
            return html.text
        except requests.exceptions.RequestException:
            i += 1

def name_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    data['类型'] = '药品'
    data['网址'] = url
    name = selector.xpath('//div[@class="drug-layout-r"]/h1/text()')
    data['名称'] = ''.join(name)
    tip = selector.xpath('//div[@class="drug-layout-r"]//p[@class="drug-layout-r-icon"]/span/text()')
    data['标签'] = ' '.join(tip)
    return data


def attribute(url):
    data = {}

    html = get_html(url)
    selector = etree.HTML(html)
    syz = selector.xpath(
        '//div[@class="drug-layout-r"]//ul[@class="drug-layout-r-ul"]//i[contains(string(),"适")]/..//p/text()')
    data['适应症'] = ''.join(syz)
    pzwh = selector.xpath(
        '//div[@class="drug-layout-r"]//ul[@class="drug-layout-r-ul"]//i[contains(string(),"批准文号")]/..//p/text()')
    data['批准文号'] = ''.join(pzwh).replace('\r', '').replace('\n', '').replace(' ', '')
    scqy = selector.xpath(
        '//div[@class="drug-layout-r"]//ul[@class="drug-layout-r-ul"]//i[contains(string(),"生产企业")]/..//a/text()')
    data['生产企业'] = ''.join(scqy).replace('\r', '').replace('\n', '').replace(' ', '')
    jg = selector.xpath(
        '//div[@class="drug-layout-r"]//ul[@class="drug-layout-r-ul"]//i[contains(string(),"价")]/..//b/text()')
    data['价格'] = ''.join(jg).replace('\r', '').replace('\n', '').replace(' ', '')
    xgjb = selector.xpath(
        '//div[@class="drug-layout-r"]//ul[@class="drug-layout-r-ul"]//i[contains(string(),"相关标签")]/..//a/text()')

    sms_url = url + 'manual/'
    sms_html = get_html(sms_url)
    sms_selector = etree.HTML(sms_html)
    zycf = sms_selector.xpath(
        '//div[@class="screen-sort-content summary-box"]//p[@class="drug-explain-tit"][contains(string(),"成份")]/..//p[@class="drug-explain-txt"]/text()')
    data['主要成分'] = ''.join(zycf).replace('\r', '').replace('\n', '').replace(' ', '')
    gnzz = sms_selector.xpath(
        '//div[@class="screen-sort-content summary-box"]//p[@class="drug-explain-tit"][contains(string(),"适应症")]/..//p[@class="drug-explain-txt"]/text()')
    data['功能主治'] = ''.join(gnzz).replace('\r', '').replace('\n', '').replace(' ', '')
    yfyl = sms_selector.xpath(
        '//div[@class="screen-sort-content summary-box"]//p[@class="drug-explain-tit"][contains(string(),"用法用量")]/..//p[@class="drug-explain-txt"]/text()')
    data['用法用量'] = ''.join(yfyl).replace('\r', '').replace('\n', '').replace(' ', '')

    total = {}
    total['属性'] = data
    total['相关疾病'] = xgjb
    return total

'''说明书'''
def intro_book(url):
    data = {}
    url = url + 'manual/'
    html = get_html(url)
    selector = etree.HTML(html)
    info_box = selector.xpath('//div[@class="screen-sort-content summary-box"]//p')
    temp_box = []
    for info in info_box:
        temp = info.xpath('string(.)').replace('\r','').replace('\n','').replace(' ','')
        temp_box.append(temp)
    data['详细说明书'] = ' '.join(temp_box)
    return data

def main(url):
    start_time = time.time()
    data = {}
    part1 = name_info(url)
    part2 = attribute(url)
    part3 = intro_book(url)
    data = {**part1,**part2,**part3}
    with open('39_drug.json', 'a+', encoding='utf-8') as f:
        json_str = json.dumps(data, ensure_ascii=False)
        f.write(json_str)
        f.write(',')
    end_time = time.time()
    print("%s已经爬取完成，耗时%fs" % (data['名称'], end_time - start_time))

#with open("39drug_url.json","r") as f:
#    urls = json.load(f)

with open('39drug_buchong_url.json','r') as f:
    urls = json.load(f)

others = urls[:-1]
last = urls[-1]

if __name__ == '__main__':
    start_time = time.time()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
#    with open('39_drug.json', 'a+') as f:
#        f.write('[')
    pool.map(main,others)
    with open('39_drug.json', 'a+') as f:
        json_str = json.dumps(main(last), ensure_ascii=False)
        f.write(json_str)
        f.write(']')
    pool.close()
    pool.join()
    end_time = time.time()
    print(end_time-start_time)
