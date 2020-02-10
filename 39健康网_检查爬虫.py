import requests
import re
import multiprocessing
import os
import time
import json
#import URLManager
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

'''名称'''
def name_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    name = selector.xpath('//div[@class="ss_det catalogItem"]//h1/b/text()')
    return ''.join(name)

'''简介'''
def introduction(url):
    html = get_html(url)
    selector = etree.HTML(html)
    basic = selector.xpath('//div[@class="ss_det catalogItem"]//div[@id="intro"]/span')
    info_box = []
    for info in basic:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    basic = ' '.join(info_box)
    return basic

'''标签'''
def tag_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    tag = selector.xpath('//div[@class="tag"]/span/a/text()')
    if tag != []:
        return tag

'''属性'''
def attribute(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    jcbw = selector.xpath('//ul[@class="infolist"]/li[contains(string(),"检查部位：")]//a/text()')
    data['检查部位'] = ''.join(jcbw)
    ks = selector.xpath('//li[contains(string(),"科室：")]//span/text()')
    data['科室'] = ''.join(ks).replace(' ', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
    if data['科室'] == '':
        ks = selector.xpath('//li[contains(string(),"科室：")]//a/text()')
        data['科室'] = ''.join(ks).replace(' ', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
    kfjc = selector.xpath('//ul[@class="infolist"]/li[contains(string(),"空腹检查：")]//span/text()')
    data['空腹检查'] = ''.join(kfjc)
    yyckbj = selector.xpath('//ul[@class="infolist"]/li[contains(string(),"医院参考价：")]//i')
    info_box = []
    for info in yyckbj:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    data['医院参考价'] = ''.join(info_box)
    bsyrq = selector.xpath('//div[@class="lbox catalogItem"]/div[contains(string(),"不适宜人群")]/../div[2]/p')
    if bsyrq != []:
        info_box = []
        for info in bsyrq:
            info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
        data['不适宜人群'] = ' '.join(info_box)
    zysx = selector.xpath('//div[@class="lbox catalogItem"]/div[contains(string(),"注意事项")]/../div[2]/p')
    info_box = []
    for info in zysx:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    data['注意事项'] = ' '.join(info_box)
    zbjd = selector.xpath('//div[@class="lbox catalogItem"]/div[contains(string(),"指标解读")]/../div[2]/p')
    info_box = []
    for info in zbjd:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    data['指标解读'] = ' '.join(info_box)
    jczy = selector.xpath('//div[@class="lbox catalogItem"]/div[contains(string(),"检查作用")]/../div[2]/p')
    info_box = []
    for info in jczy:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    data['检查作用'] = ' '.join(info_box)
    jcgc = selector.xpath('//div[@class="lbox catalogItem"]/div[contains(string(),"检查过程")]/../div[2]/p')
    info_box = []
    for info in jcgc:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    data['检查过程'] = ' '.join(info_box)
    return data


'''相关疾病&相关症状'''


def related_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    temp = {}

    xgjb_title = selector.xpath(
        '//div[@class="lbox catalogItem"]/div[contains(string(),"相关疾病")]/../div[2]//ul/li/a/text()')
    xgjb_href = selector.xpath(
        '//div[@class="lbox catalogItem"]/div[contains(string(),"相关疾病")]/../div[2]//ul/li/a//@href')
    xgjb_box = []
    for i in range(len(xgjb_title)):
        data = {}
        data['名称'] = xgjb_title[i]
        data['网址'] = xgjb_href[i]
        xgjb_box.append(data)
    temp['相关疾病'] = xgjb_box

    xgzz_title = selector.xpath(
        '//div[@class="lbox catalogItem"]/div[contains(string(),"相关症状")]/../div[2]//ul/li/a/text()')
    xgzz_href = selector.xpath(
        '//div[@class="lbox catalogItem"]/div[contains(string(),"相关症状")]/../div[2]//ul/li/a//@href')
    xgzz_box = []
    for i in range(len(xgzz_title)):
        data = {}
        data['名称'] = xgzz_title[i]
        data['网址'] = xgzz_href[i]
        xgzz_box.append(data)
    temp['相关症状'] = xgzz_box

    return temp

#with open('39url_check.json', 'r') as f:
#    urls = json.load(f)

with open("39check_buchong_url.json","r") as f:
    urls = json.load(f)

others = urls[:-1]
last = urls[-1]

def main(url):
    start_time = time.time()
    data = {}
    data['类型'] = '检查'
    data['网址'] = url
    data['名称'] = name_info(url)
    data['简介'] = introduction(url)
    data['标签'] = tag_info(url)
    data['属性'] = attribute(url)
    data = {**data,**related_info(url)}
    with open('39_check.json', 'a+', encoding='utf-8') as f:
        json_str = json.dumps(data, ensure_ascii=False)
        f.write(json_str)
        f.write(',')
    end_time = time.time()
    print("%s已经爬取完成，耗时%fs"%(data['名称'],end_time-start_time))
    return data

if __name__ == '__main__':
    start_time = time.time()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
#    with open('39_check.json', 'a+') as f:
#        f.write('[')
    pool.map(main,others)
    with open('39_check.json', 'a+') as f:
        json_str = json.dumps(main(last), ensure_ascii=False)
        f.write(json_str)
        f.write(']')
    pool.close()
    pool.join()
    end_time = time.time()
    print(end_time-start_time)