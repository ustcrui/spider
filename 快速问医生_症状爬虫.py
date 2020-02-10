import requests
import re
import multiprocessing
import os
import time
import json
from lxml import etree
from urllib import parse

'''根据url解析页面'''
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

'''获取症状名称'''
def name_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    name = selector.xpath('//div[@class="disease-cont"]//strong/text()')
    return ''.join(name)

'''获取症状简介'''
def basic_info(url):
    gaishu_url = url + 'gaishu/'
    html = get_html(gaishu_url)
    selector = etree.HTML(html)
    basic_info = selector.xpath('//div[@class="symptom-box-left-details"]')
    infobox = []
    for info in basic_info:
        infobox.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    basic_info = ' '.join(infobox)
    return basic_info

'''处理症状概括信息的工具'''
def gaikuo_tool(url):
    html = get_html(url)
    selector = etree.HTML(html)
    content = selector.xpath('//div[@class="symptom-box-left-details"]')
    info_box = []
    for info in content:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    info_box = ' '.join(info_box)
    return info_box
'''获取症状概括信息'''
def gaikuo_info(url):
    reason_url = url + 'bingyin/'           #病因
    check_url = url + 'jiancha/'            #检查
    identify_url = url + 'jianbie/'         #鉴别
    prevent_url = url + 'yufang/'           #预防
    treat_url = url + 'huanjie/'            #缓解
    reason = gaikuo_tool(reason_url)
    check = gaikuo_tool(check_url)
    identify = gaikuo_tool(identify_url)
    prevent = gaikuo_tool(prevent_url)
    treat = gaikuo_tool(treat_url)
    data = {}
    data['病因'] = reason
    data['检查'] = check
    data['鉴别'] = identify
    data['预防'] = prevent
    data['缓解'] = treat
    return data

'''饮食禁忌'''
def food_info(url):
    shiliao_url = url + 'shiliao/'
    shiliao_html = get_html(shiliao_url)
    shiliao_selector = etree.HTML(shiliao_html)
    data = {}
    suit = shiliao_selector.xpath('//div[@class="container-1"]//span')
    unsuit = shiliao_selector.xpath('//div[@class="container-2"]//span')
    suit_box = []
    for su in suit:
        suit_box.append(su.xpath('string(.)').replace('\n',''))
    data['饮食宜'] = ''.join(suit_box)
    unsuit_box = []
    for un in unsuit:
        unsuit_box.append(un.xpath('string(.)').replace('\n',''))
    data['饮食忌'] = ''.join(unsuit_box)
    return data

'''综合属性值'''
def attribute(url):
    gk = gaikuo_info(url)
    ys = food_info(url)
    connect = {**gk,**ys}
    return connect

'''相关疾病症状'''
def related_disease(url):
    html = get_html(url)
    selector = etree.HTML(html)
    title = selector.xpath('//div[@class="disease-related-list clears"]/a/text()')
    href = selector.xpath('//div[@class="disease-related-list clears"]//@href')
    related_disease_list = []
    for i in range(len(title)):
        data = {}
        data['名称'] = title[i]
        data['网址'] = href[i]
        related_disease_list.append(data)
    return related_disease_list

'''可能患有疾病'''
def possible_sick(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data_list = []
    name_list = []
    name = selector.xpath('//div[@class="possible-sick"]//span[@class="sp1"]')
    for info in name:
        name_list.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    length = len(name_list)-1
    for i in range(length):
        data = {}
        sympton_list = []
        href_black = selector.xpath('//div[@class="possible-sick"]//li[%d]/span[@class="sp1"]/a/@href'%(i+1))
        department_black = selector.xpath('//div[@class="possible-sick"]//li[%d]/span[@class="sp2"]/a/text()'%(i+1))
        sympton_black = selector.xpath('//div[@class="possible-sick"]//li[%d]/span[@class="sp3"]/a/text()'%(i+1))
        for info in sympton_black:
            sympton_list.append(info.replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
        data['名称'] = name_list[i+1]
        data['网址'] = '、'.join(href_black)
        data['就诊科室'] = '、'.join(department_black)
        data['典型症状'] = sympton_list
        data_list.append(data)
    return data_list

'''可能患有疾病_全'''
def total_possible(url):
    url = url + 'jibing/'
    html = get_html(url)
    selector = etree.HTML(html)
    possible = []
    title = selector.xpath('//div[@class="programme-cont-page internal-medicine jibing-box"]//a/text()')
    href = selector.xpath('//div[@class="programme-cont-page internal-medicine jibing-box"]//@href')
    for i in range(len(title)):
        data = {}
        data['名称'] = title[i]
        data['网址'] = href[i]
        possible.append(data)
    return possible

'''根据url获取症状所有信息'''
def main(url):
    start = time.time()
    data = {}
    data['类型'] = "症状"
    data['网址'] = url
    data['名称'] = name_info(url)
    data['简介'] = basic_info(url)
    data['属性'] = attribute(url)
    data['相关疾病'] = related_disease(url)
    data['可能患有疾病'] = possible_sick(url)
    data['可能患有疾病_全'] = total_possible(url)
    end = time.time()
    take_time = end-start
    print('%s已爬取完成,用时%f秒'%(data['名称'],take_time))
    return data

'''按照拼音获取所有症状链接'''
main_html = get_html('https://tag.120ask.com/zhengzhuang/pinyin/a.html')
main_selector = etree.HTML(main_html)
main_list = main_selector.xpath('//div[@class="programme-cont-page internal-medicine"]//h1//@href')
urls = []
for url in main_list:
    html = get_html('http://tag.120ask.com' + url)
    selector = etree.HTML(html)
    href = selector.xpath('//div[@class="programme-cont-page internal-medicine"]/div//@href')
    for hr in href:
        urls.append('http://tag.120ask.com' + hr)

#test_url = []
#for i in range(20):
#   test_url.append(urls[i])

if __name__ == '__main__':
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    medical = pool.map(main,urls)
    with open('symptom.json','w',encoding='utf-8') as f:
        json_str = json.dumps(medical,ensure_ascii=False)
        f.write(json_str)
    pool.close()
    pool.join()
