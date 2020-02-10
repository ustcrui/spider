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
    html = requests.get(url=url , headers= headers, proxies=proxies)
    html.encoding = 'utf-8'
    return html.text

'''名称'''
def name_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    name = selector.xpath('//header[@class="list_tit"]/div//h1/text()')
    return ''.join(name)

'''简介'''
def introduction(url):
    html = get_html(url)
    selector = etree.HTML(html)
    basic = selector.xpath('//div[@class="intro clearfix"]//dd[@id="intro"]/p')
    info_box = []
    for info in basic:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    basic = ' '.join(info_box)
    return basic


'''属性'''


def attribute(url):
    data = {}

    # 症状起因
    zzqy_url = url + 'zzqy/'
    html = get_html(zzqy_url)
    selector = etree.HTML(html)
    zzqy = selector.xpath('//div[@class="item catalogItem"]/p')
    info_box = []
    for info in zzqy:
        info_box.append(
            info.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace(
                '\t', '').replace('\u3000', ''))
    zzqy = ' '.join(info_box)
    data['症状起因'] = zzqy

    # 诊断详述
    zdxs_url = url + 'zdxs/'
    html = get_html(zdxs_url)
    selector = etree.HTML(html)
    zdxs = selector.xpath('//div[@class="item catalogItem"]/p')
    info_box = []
    for info in zdxs:
        info_box.append(
            info.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace(
                '\t', '').replace('\u3000', ''))
    zdxs = ' '.join(info_box)
    data['诊断详述'] = zdxs

    # 就诊指南
    jzzn_url = url + 'jzzn/'
    html = get_html(jzzn_url)
    selector = etree.HTML(html)
    jzzn = selector.xpath('//div[@class="zn-main"]/dl')
    info_box = []
    for info in jzzn:
        info_box.append(
            info.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace(
                '\t', '').replace('\u3000', ''))
    jzzn = ' '.join(info_box)
    data['就诊指南'] = jzzn

    return data

'''可能疾病'''
def possible_disease(url):
    url = url + 'zzqy/'
    html = get_html(url)
    selector = etree.HTML(html)
    possible = []
    title = selector.xpath('//div[@class="item"]//tr[position()>1]/td[1]//@title')
    href = selector.xpath('//div[@class="item"]//tr[position()>1]/td[1]//@href')
    for i in range(len(title)):
        data = {}
        data['名称'] = title[i]
        data['网址'] = href[i]
        possible.append(data)
    return possible

'''对症药品'''
def related_drug(url):
    html = get_html(url)
    selector = etree.HTML(html)
    drug = []
    title = selector.xpath('//div[@class="lbox catalogItem"]//dl/dd/h4/a//@title')
    href = selector.xpath('//div[@class="lbox catalogItem"]//dl/dd/h4/a//@href')
    for i in range(len(title)):
        data = {}
        if title[i] != '':
            data['名称'] = title[i]
            data['网址'] = href[i]
            drug.append(data)
    return drug

'''常见检查'''
def check_info(url):
    url = url + 'jcjb/'
    html = get_html(url)
    selector = etree.HTML(html)
    check = []
    title = selector.xpath('//div[@class="checkbox-data"]//tr[position()>1]/td[1]/a/text()')
    href = selector.xpath('//div[@class="checkbox-data"]//tr[position()>1]/td[1]/a//@href')
    for i in range(len(title)):
        data = {}
        data['名称'] = title[i]
        data['网址'] = href[i]
        check.append(data)
    return check

'''具体种类'''
def types_info(url):
    url = url + 'jcjb/'
    html = get_html(url)
    selector = etree.HTML(html)
    type_list = []
    types = selector.xpath('//div[@class="item"]/h4/text()')
    if types != []:
        title = selector.xpath('//div[@class="item"]//dl[@class="item"]/dt/a//@title')
        href = selector.xpath('//div[@class="item"]//dl[@class="item"]/dt/a//@href')
        for i in range(len(title)):
            data = {}
            data['名称'] = title[i]
            data['网址'] = href[i]
            type_list.append(data)
        data = {}
        data['相似症状'] = type_list
        return data

def main(url):
    start_time = time.time()
    data = {}
    data['类型'] = '症状'
    data['网址'] = url
    data['名称'] = name_info(url)
    data['简介'] = introduction(url)
    data['属性'] = attribute(url)
    data['可能疾病'] = possible_disease(url)
    data['对症药品'] = related_drug(url)
    data['常见检查'] = check_info(url)
    xszz = types_info(url)
    if xszz != None:
        data = {**data,**xszz}
    end_time = time.time()
    print("%s已经爬取完成，耗时%fs"%(data['名称'],end_time-start_time))
    return data

with open('39url_symptom.json', 'r') as f:
    urls = json.load(f)

#test_url = []
#for i in range(100):
#   test_url.append(urls[i])

if __name__ == '__main__':
    start_time = time.time()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    disease = pool.map(main,urls)
    with open('39url_symptom.json','w',encoding='utf-8') as f:
        json_str = json.dumps(disease,ensure_ascii=False)
        f.write(json_str)
    pool.close()
    pool.join()
    end_time = time.time()
    print(end_time-start_time)