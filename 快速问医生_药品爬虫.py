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
    i = 0
    while i < 3:
        try:
            html = requests.get(url=url, headers=headers, proxies=proxies, timeout=5)
            html.encoding = 'utf-8'
            return html.text
        except requests.exceptions.RequestException:
            i += 1

'''药品名称'''
def name_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    data['类型'] = "药品"
    data['网址'] = url
    name = selector.xpath('//div[@class="details-right-drug"]/p[not(@class)]/text()')
    data['名称'] =  ''.join(name)
    price = selector.xpath('//div[@class="details-right-drug"]//div[@class="Drugs-Price"]//span/text()')
    data['参考价'] = ''.join(price)
    return data

def related_disease(url):
    html = get_html(url)
    selector = etree.HTML(html)
    disease = selector.xpath('//div[@class="details-right-drug"]//li[contains(string(),"相关疾病：")]/var//@onclick')
    info_box = []
    for info in disease:
        info_box.append(re.sub("[A-Za-z0-9\(\')']", "", info))
    return info_box

'''药品详情'''
def detail_info(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    spmc = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"商品名称")]/var/text()')
    tymc = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"通用名称")]/var/text()')
    ywm = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"英文名")]/var/text()')
    pzwh = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"批准文号")]/var/text()')
    gg = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"规格")]/var/text()')
    bz = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"包装")]/var/text()')
    yfyl = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"用法用量")]/var/text()')
    fl = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"分类")]/var/text()')
    lx = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"类型")]/var/text()')
    yb = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"医保")]/var/text()')
    jx = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"剂型")]/var/text()')
    xz = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"性状")]/var/text()')
    wyy = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"外用药")]/var/text()')
    yxq = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"有效期")]/var/text()')
    country = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"国家/地区")]/var/text()')
    scqy = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-1 tab-dm-1"]//p[contains(string(),"生产企业")]/var/text()')
    data['商品名称'] = ''.join(spmc).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['通用名称'] = ''.join(tymc).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['英文名'] = ''.join(ywm).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['批准文号'] = ''.join(pzwh).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['规格'] = ''.join(gg).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['包装'] = ''.join(bz).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['用法用量'] = ''.join(yfyl).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['分类'] = ''.join(fl).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['类型'] = ''.join(lx).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['医保'] = ''.join(yb).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['剂型'] = ''.join(jx).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['性状'] = ''.join(xz).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['外用药'] = ''.join(wyy).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['有效期'] = ''.join(yxq).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['国家/地区'] = ''.join(country).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    data['生产企业'] = ''.join(scqy).replace('\r','').replace('\n','').replace('\xa0','').replace('   ', '').replace('\t','').replace('\u3000','')
    return data


'''药品说明书'''
def introduction(url):
    html = get_html(url)
    selector = etree.HTML(html)
    data = {}
    spmc = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"商品名称")]/var/text()')
    tymc = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"通用名称")]/var/text()')
    zycf = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"主要成份")]/var/text()')
    syz = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"适应症")]/var/text()')
    blfy = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"不良反应")]/var/text()')
    jj = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"禁忌")]/var/text()')
    zysx = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"注意事项")]/var/text()')
    yf = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"孕妇及哺乳期妇女用药")]/var/text()')
    ertong = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"儿童用药")]/var/text()')
    lr = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"老人用药")]/var/text()')
    ywgl = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"药物过量")]/var/text()')
    ywdl = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"药物毒理")]/var/text()')
    yddlx = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"药代动力学")]/var/text()')
    zc = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"贮藏")]/var/text()')
    zxbz = selector.xpath('//div[@class="cont-Drug-details"]//div[@class="cont-2 tab-dm-2"]//p[contains(string(),"执行标准")]/var/text()')

    data['商品名称'] = ''.join(spmc).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    data['通用名称'] = ''.join(tymc).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    data['主要成份'] = ''.join(zycf).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    data['适应症'] = ''.join(syz).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t','').replace('\u3000', '')
    data['不良反应'] = ''.join(blfy).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    data['禁忌'] = ''.join(jj).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t','').replace('\u3000', '')
    data['注意事项'] = ''.join(zysx).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    data['孕妇及哺乳期妇女用药'] = ''.join(yf).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    data['儿童用药'] = ''.join(ertong).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    data['老人用药'] = ''.join(lr).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t','').replace('\u3000', '')
    data['药物过量'] = ''.join(ywgl).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    data['药物毒理'] = ''.join(ywdl).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    data['药代动力学'] = ''.join(yddlx).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    data['贮藏'] = ''.join(zc).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t','').replace('\u3000', '')
    data['执行标准'] = ''.join(zxbz).replace('\r', '').replace('\n', '').replace('\xa0', '').replace('   ', '').replace('\t', '').replace('\u3000', '')
    return data

#with open("drug_url.json","r") as f:
#    drugs = json.load(f)

#with open("new_drug.json","r") as f:
#    drugs = json.load(f)

with open("buchong_url.json","r") as f:
    drugs = json.load(f)

others = drugs[:-1]
last = drugs[-1]

def main(url):
    start = time.time()
    data = {}
    name = name_info(url)
    data['相关疾病'] = related_disease(url)
    data['药品详情'] = detail_info(url)
    data['药品说明书'] = introduction(url)
    data = {**name,**data}
    with open('new_drug.json','a+',encoding='utf-8') as f:
        json_str = json.dumps(data,ensure_ascii=False)
        f.write(json_str)
        f.write(',')
    with open('buchong_crawled_url.json','a+',encoding='utf-8') as f:
        json_str = json.dumps(url)
        f.write(json_str)
        f.write(',')
    end = time.time()
    take_time = end-start
    print('%s已爬取完成,用时%f秒'%(data['名称'],take_time))
    return data

if __name__ == '__main__':
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
#    with open('drug.json', 'a+') as f:
#        f.write('[')
    pool.map(main,others)
    with open('new_drug.json','a+',encoding='utf-8') as f:
        json_str = json.dumps(main(last),ensure_ascii=False)
        f.write(json_str)
        f.write(']')
    pool.close()
    pool.join()
