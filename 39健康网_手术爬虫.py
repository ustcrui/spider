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
    name = selector.xpath('//div[@class="ss_det catalogItem"]//h1/b/text()')
    return ''.join(name)

'''简介'''
def introduction(url):
    html = get_html(url)
    selector = etree.HTML(html)
    basic = selector.xpath('//div[@class="ss_det catalogItem"]//div[@id="intro1"]/span')
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
    jcbw = selector.xpath('//li[contains(string(),"手术部位：")]//a/text()')
    data['手术部位'] = ''.join(jcbw)
    ks = selector.xpath('//li[contains(string(),"科室：")]//span/text()')
    data['科室'] = ''.join(ks).replace(' ', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
    if data['科室'] == '':
        ks = selector.xpath('//li[contains(string(),"科室：")]//a/text()')
        data['科室'] = ''.join(ks).replace(' ', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
    sssj = selector.xpath('//li[contains(string(),"手术时间：")]//span/text()')
    data['手术时间'] = ''.join(sssj).replace(' ', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
    mzfs = selector.xpath('//li[contains(string(),"麻醉方式：")]//span/text()')
    data['麻醉方式'] = ''.join(mzfs).replace(' ', '').replace('\r', '').replace('\n', '').replace('\xa0', '')
    yyckbj = selector.xpath('//li[contains(string(),"医院参考价：")]//i')
    info_box = []
    for info in yyckbj:
        info_box.append(
            info.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace(
                '\t', '').replace('\u3000', ''))
    data['医院参考价'] = ''.join(info_box)

    bsyrq = selector.xpath('//div[@class="lbox catalogItem"]/div[contains(string(),"不适宜人群")]/../div[2]/p')
    if bsyrq != []:
        info_box = []
        for info in bsyrq:
            info_box.append(
                info.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ',
                                                                                                        '').replace(
                    '\t', '').replace('\u3000', ''))
        data['不适宜人群'] = ' '.join(info_box)

    syz = selector.xpath('//div[@class="lbox catalogItem"]/div[contains(string(),"注意事项")]/../div[2]/p')
    info_box = []
    for info in syz:
        info_box.append(
            info.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace(
                '\t', '').replace('\u3000', ''))
    data['适应症'] = ' '.join(info_box)

    sq = selector.xpath('//div[@class="lbox catalogItem"]/div[contains(string(),"术前")]/../div[position()>1]/p')
    info_box = []
    for info in sq:
        info_box.append(
            info.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace(
                '\t', '').replace('\u3000', ''))
    data['术前'] = ' '.join(info_box)

    sh = selector.xpath('//div[@class="lbox catalogItem"]/div[contains(string(),"术后")]/../div[position()>1]/p')
    info_box = []
    for info in sh:
        info_box.append(
            info.xpath('string(.)').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace(
                '\t', '').replace('\u3000', ''))
    data['术后'] = ' '.join(info_box)

    return data


'''相关疾病'''


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

    return temp

def main(url):
    start_time = time.time()
    data = {}
    data['类型'] = '手术'
    data['网址'] = url
    data['名称'] = name_info(url)
    data['简介'] = introduction(url)
    data['标签'] = tag_info(url)
    data['属性'] = attribute(url)
    data = {**data,**related_info(url)}
    end_time = time.time()
    print("%s已经爬取完成，耗时%fs"%(data['名称'],end_time-start_time))
    return data

with open('39url_operation.json', 'r') as f:
    urls = json.load(f)

#test_url = []
#for i in range(100):
#   test_url.append(urls[i])

if __name__ == '__main__':
    start_time = time.time()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    disease = pool.map(main,urls)
    with open('39_operation.json','w',encoding='utf-8') as f:
        json_str = json.dumps(disease,ensure_ascii=False)
        f.write(json_str)
    pool.close()
    pool.join()
    end_time = time.time()
    print(end_time-start_time)