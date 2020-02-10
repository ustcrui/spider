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
    name = selector.xpath('//div[@class="disease"]/h1/text()')
    return ''.join(name)

'''简介'''
def introduction(url):
    url = url + 'jbzs/'
    html = get_html(url)
    selector = etree.HTML(html)
    basic = selector.xpath('//div[@class="list_left"]//p[@class="introduction"]')
    info_box = []
    for info in basic:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    basic = ' '.join(info_box)
    return basic

'''基本知识'''
def basic_info(url):
    url = url + 'jbzs/'
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    yibao_box = []
    bieming_box = []
    fbbw_box = []
    crx_box = []
    dfrq_box = []
    related_symptom = []
    yibao = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"是否属于医保：")]//span[2]')
    bieming = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"别名：")]//span[2]')
    fbbw = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"发病部位：")]//span[2]')
    crx = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"传染性：")]//span[2]')
    dfrq = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"多发人群：")]//span[2]')
    for info in yibao:
        yibao_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    data['是否属于医保'] = ''.join(yibao_box)
    for info in bieming:
        bieming_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    data['别名'] = ''.join(bieming_box).replace('\n','').replace(' ','')
    for info in fbbw:
        fbbw_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    data['发病部位'] = ''.join(fbbw_box).replace('\n','').replace(' ','')
    for info in crx:
        crx_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    data['传染性'] = ''.join(crx_box).replace('\n','').replace(' ','')
    for info in dfrq:
        dfrq_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    data['多发人群'] = ''.join(dfrq_box).replace('\n','').replace(' ','')
    symptom_title = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"相关症状：")]//a[@class]/text()')
    symptom_href = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"相关症状：")]//a[@class]//@href')
    if symptom_title != []:
        for i in range(len(symptom_title)):
            temp = {}
            temp['名称'] = symptom_title[i]
            temp['网址'] = symptom_href[i]
            related_symptom.append(temp)
    data['相关症状'] = related_symptom
    return data

'''诊疗知识'''
def treat_info(url):
    url = url + 'jbzs/'
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    bfjb = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"并发疾病：")]//a[@class]/text()')[:-1]
    data['并发疾病'] = '、'.join(bfjb).replace('\n','').replace(' ','')
    jzks = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"就诊科室：")]//a/text()')
    data['就诊科室'] = '、'.join(jzks).replace('\n','').replace(' ','')
    zlfy = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"治疗费用：")]//span[2]/text()')
    data['治疗费用'] = '、'.join(zlfy).replace('\n','').replace(' ','')
    zlzq = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"治疗周期：")]//span[2]/text()')
    data['治疗周期'] = '、'.join(zlzq).replace('\n','').replace(' ','')
    zlff = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"治疗方法：")]//a[@class]/text()')[:-1]
    data['治疗方法'] = '、'.join(zlff).replace('\n','').replace(' ','')
    xgjc = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"相关检查：")]//a[@class]/text()')[:-1]
    data['相关检查'] = '、'.join(xgjc).replace('\n','').replace(' ','')
    cyyp_title = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"常用药品：")]//a[@href]/text()')[:-1]
    cyyp_href = selector.xpath('//ul[@class="disease_basic"]//li[contains(string(),"常用药品：")]//a[@href]//@href')[:-1]
    cyyp = []
    for i in range(len(cyyp_title)):
        cyyp_data = {}
        cyyp_data['名称'] = cyyp_title[i]
        cyyp_data['网址'] = cyyp_href[i]
        cyyp.append(cyyp_data)
    data['常用药品'] = cyyp
    return data

'''具体种类或者类似疾病'''
def types_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    info_box = {}
    data = []
    types = selector.xpath('//div[@class="disease_box"][2]/p/text()')
    title = selector.xpath('//div[@class="disease_box"][2]//li/a/text()')
    href = selector.xpath('//div[@class="disease_box"][2]//li/a//@href')
    for i in range(len(title)):
        info = {}
        info['名称'] = title[i]
        info['网址'] = href[i]
        data.append(info)
    if ''.join(types) == '其他类似疾病 ':
        info_box['类似疾病'] = data
    else:
        info_box['具体种类'] = data
    return info_box

'''去医院必看'''
def readfirst(url):
    url = url + 'jbzs/'
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    zjjzsj = selector.xpath('//div[@class="list_left"]/div[4]//li[contains(string(),"最佳就诊时间：")]/span[2]/text()')
    jzsc = selector.xpath('//div[@class="list_left"]/div[4]//li[contains(string(),"就诊时长：")]/span[2]/text()')
    zlzq = selector.xpath('//div[@class="list_left"]/div[4]//li[contains(string(),"复诊频率/治疗周期：")]/span[2]/text()')
    jzqzb = selector.xpath('//div[@class="list_left"]/div[4]//li[contains(string(),"就诊前准备：")]/span[2]/text()')
    data['最佳就诊时间：'] = ''.join(zjjzsj).replace('\n','').replace(' ','')
    data['就诊时长：'] = ''.join(jzsc).replace('\n','').replace(' ','')
    data['复诊频率/治疗周期：'] = ''.join(zlzq).replace('\n','').replace(' ','')
    data['就诊前准备：'] = ''.join(jzqzb).replace('\n','').replace(' ','')
    return data

'''属性'''
def attribute(url):
    bs = basic_info(url)
    tr = treat_info(url)
    rf = readfirst(url)
    return {**bs,**tr,**rf}

def main(url):
    start = time.time()
    data = {}
    data['类型'] = '疾病'
    data['网址'] = url
    data['名称'] = name_info(url)
    data['属性'] = attribute(url)
    types = types_info(url)
    data = {**data,**types}
    end = time.time()
    take_time = end - start
    print('%s已爬取完成,用时%f秒' % (data['名称'], take_time))
    return data

with open('39_url.json', 'r') as f:
    urls = json.load(f)

#test_url = []
#for i in range(10):
#   test_url.append(urls[i])

if __name__ == '__main__':
    start_time = time.time()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    disease = pool.map(main,urls)
    with open('39_disease.json','w',encoding='utf-8') as f:
        json_str = json.dumps(disease,ensure_ascii=False)
        f.write(json_str)
    pool.close()
    pool.join()
    end_time = time.time()
    print(end_time-start_time)

