import requests
import json
import time
import urllib.request
import urllib.parse
from lxml import etree
import multiprocessing
import pymongo
import re

'''根据url解析网页'''
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

'''获取疾病名称'''
def name_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    name = selector.xpath('//div[@class="disease-cont"]//strong/text()')
    return name[0]

'''获取疾病简介'''
def basic_info(url):
    gaishu_url = url + 'gaishu/'
    html = get_html(gaishu_url)
    selector = etree.HTML(html)
    basic_info = selector.xpath('//div[@class="art_cont"]')
    infobox = []
    for info in basic_info:
        infobox.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    basic_info = ' '.join(infobox)
    return basic_info

'''去医院必看'''
'''去医院必看'''
def bikan_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    data['挂什么科'] = ' '.join(selector.xpath('//div[@class="disease-list-left"]//li[1]//var/text()'))
    data['哪些症状'] = ' '.join(selector.xpath('//div[@class="disease-list-left"]//li[2]//var/text()'))
    data['好发人群'] = ' '.join(selector.xpath('//div[@class="disease-list-left"]//li[3]//var/text()'))
    data['需作检查'] = ' '.join(selector.xpath('//div[@class="disease-list-left"]//li[4]//var/text()'))
    data['引发疾病'] = ' '.join(selector.xpath('//div[@class="disease-list-left"]//li[5]//var/text()'))
    data['治疗方法'] = ' '.join(selector.xpath('//div[@class="disease-list-left"]//li[6]//var/text()'))
    return data

'''就医小贴士'''
def tieshi_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    data['常用药物'] = ' '.join(selector.xpath('//div[@class="disease-list-center"]//li[position()=1]/var/text()'))
    data['治疗费用'] = ' '.join(selector.xpath('//div[@class="disease-list-center"]//li[position()=2]/var/text()'))
    data['是否传染'] = ' '.join(selector.xpath('//div[@class="disease-list-center"]//li[position()=3]/var/text()'))
    data['患病比例'] = ' '.join(selector.xpath('//div[@class="disease-list-center"]//li[position()=4]/var/text()'))
    data['治愈率'] = ' '.join(selector.xpath('//div[@class="disease-list-center"]//li[position()=5]/var/text()'))
    data['治疗周期'] = ' '.join(selector.xpath('//div[@class="disease-list-center"]//li[position()=6]/var/text()'))
    return data

'''饮食禁忌'''
def food_info(url):
    shiliao_url = url + 'shiliao/'
    shiliao_html = get_html(shiliao_url)
    shiliao_selector = etree.HTML(shiliao_html)
    data = {}
    suit = shiliao_selector.xpath('//div[@class="dl_1"]//var')
    unsuit = shiliao_selector.xpath('//div[@class="dl_2"]//var')
    suit_box = []
    for su in suit:
        suit_box.append(su.xpath('string(.)').replace('\n',''))
    data['饮食宜'] = ''.join(suit_box)
    unsuit_box = []
    for un in unsuit:
        unsuit_box.append(un.xpath('string(.)').replace('\n',''))
    data['饮食忌'] = ''.join(unsuit_box)
    return data

'''处理疾病概括信息的工具'''
def gaikuo_tool(url):
    html = get_html(url)
    selector = etree.HTML(html)
    content = selector.xpath('//div[@class="art_cont"]')
    info_box = []
    for info in content:
        info_box.append(info.xpath('string(.)').replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000',''))
    info_box = ' '.join(info_box)
    return info_box
'''获取疾病概括信息'''
def gaikuo_info(url):
    reason_url = url + 'bingyin/'           #病因
    symptom_url = url + 'zhengzhuang/'      #症状
    check_url = url + 'jiancha/'            #检查
    identify_url = url + 'jianbie/'         #鉴别
    illness_url = url + 'bingfa/'      #病发症
    prevent_url = url + 'yufang/'           #预防
    treat_url = url + 'zhiliao/'            #治疗
    diet_url = url + 'yinshi/'              #饮食
    reason = gaikuo_tool(reason_url)
    symptom = gaikuo_tool(symptom_url)
    check = gaikuo_tool(check_url)
    identify = gaikuo_tool(identify_url)
    illness = gaikuo_tool(illness_url)
    prevent = gaikuo_tool(prevent_url)
    treat = gaikuo_tool(treat_url)
    diet = gaikuo_tool(diet_url)
    data = {}
    data['病因'] = reason
    data['症状'] = symptom
    data['检查'] = check
    data['鉴别'] = identify
    data['并发症'] = illness
    data['预防'] = prevent
    data['治疗'] = treat
    data['饮食'] = diet
    return data

'''根据一个网页获取相关属性信息'''
def attribute(url):
    bk = bikan_info(url)
    ts = tieshi_info(url)
    f = food_info(url)
    gk = gaikuo_info(url)
    connect = {**bk,**ts,**f,**gk}
    return connect

'''相关疾病症状'''
def related_disease(url):
    html = get_html(url)
    selector = etree.HTML(html)
    title = selector.xpath('//div[@class="disease-Related-List clear"]/a/text()')
    href = selector.xpath('//div[@class="disease-Related-List clear"]//@href')
    related_disease_list = []
    for i in range(len(title)):
        data = {}
        data['名称'] = title[i]
        data['网址'] = href[i]
        related_disease_list.append(data)
    return related_disease_list

'''推荐好药'''
def drug(url):
    html = get_html(url)
    selector = etree.HTML(html)
    title = selector.xpath('//div[@class="clear img-list"]//span/text()')
    href = selector.xpath('//div[@class="clear img-list"]//@href')
    drug_list = []
    for i in range(len(title)):
        data = {}
        data['名称'] = title[i]
        data['网址'] = href[i]
        drug_list.append(data)
    return drug_list

'''主函数，针对一个网页爬取所有相关信息'''
def main(url):
    start = time.time()
    data = {}
    data['类型'] = "疾病"
    data['网址'] = url
    data['名称'] = name_info(url)
    data['简介'] = basic_info(url)
    data['属性'] = attribute(url)
    data['相关症状'] = related_disease(url)
    data['推荐药品'] = drug(url)
    end = time.time()
    take_time = end-start
    print('%s已爬取完成,用时%f秒'%(data['名称'],take_time))
    return data

'''按照拼音获取所有疾病链接'''
html = get_html('http://tag.120ask.com/jibing/pinyin/a.html')
selector = etree.HTML(html)
main_list = selector.xpath('//div[@class="sick_tag"]/span//@href')
urls = []
for list in main_list:
    main_html = get_html('http://tag.120ask.com/'+list)
    main_selector = etree.HTML(main_html)
    href = main_selector.xpath('//div[@class="tag_li"]//@href')
    for i in range(len(href)):
        urls.append('http://tag.120ask.com/' + href[i])
# len(urls) = 9618

#test_url = []
#for i in range(10):
#    test_url.append(urls[i])

if __name__ == '__main__':
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    medical = pool.map(main,urls)
    with open('disease.json','w',encoding='utf-8') as f:
        json_str = json.dumps(medical,ensure_ascii=False)
        f.write(json_str)
    pool.close()
    pool.join()
