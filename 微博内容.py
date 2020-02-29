import selenium
import time
import os
from tqdm import *
import json
import random
import time
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from apscheduler.schedulers.blocking import BlockingScheduler

def get_weiboList(driver):
    retList = driver.find_element_by_xpath('/html[1]/body[1]/div[1]/div[1]/div[1]').find_elements_by_class_name('card9')
    return retList

def get_content(driver, path):
    for i in range(3):
        js = 'window.open("%s")' % path
        driver.execute_script(js)
        driver.switch_to.window(driver.window_handles[1])
        try:
            text = driver.find_element_by_xpath('//div[@class="weibo-og"]').text
        except:
            text = None
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        if text != None:
            break
    return text

def start_chrome(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options = options) 
    driver.get(url)
    driver.implicitly_wait(5)     #所有页面隐性等待
    return driver

def info_spider(driver):
    data = {}
    info_box = driver.find_element_by_xpath('//div[@class="item-list"]')
    name = info_box.find_element_by_xpath('div/span/span').text
    subscribe = info_box.find_element_by_xpath('div[2]/div/span').text
    fans = info_box.find_element_by_xpath('div[2]/div[2]/span').text
    data['user_name'] = name
    data['关注'] = subscribe
    data['粉丝'] = fans
    return data

def crwal_spider(driver, weibo):
    data = {}
    text = weibo.find_element_by_xpath('div//div[@class="weibo-og"]').text
    if "...全文" in text:
        href = weibo.find_element_by_xpath('div//div[@class="weibo-og"]/div[1]/a[last()]').get_attribute('href')
        content = get_content(driver, href)
        data['正文'] = content
    else:
        data['正文'] = text
    
    try:
        rp_text = weibo.find_element_by_xpath('div//div[@class="weibo-rp"]//div[@class="weibo-text"]/span[2]').text
        if "...全文" in rp_text:
            link = weibo.find_element_by_xpath(
                'div//div[@class="weibo-rp"]//div[@class="weibo-text"]/span[2]/a[last()]').get_attribute('href')
            data['转发内容'] = get_content(driver, link)
        else:
            data['转发内容'] = rp_text
    except:
        pass
    
    zhuan = weibo.find_element_by_xpath('div//footer/div[1]/h4').text
    ping = weibo.find_element_by_xpath('div//footer/div[2]/h4').text
    dian = weibo.find_element_by_xpath('div//footer/div[3]/h4').text
    time = weibo.find_element_by_xpath('div//header//span[@class="time"]').text
    if dian == '赞':
        data['点赞'] = '0'
    else:
        data['点赞'] = dian
    if ping == '评论':
        data['评论'] = '0'
    else:
        data['评论'] = ping
    if zhuan == '转发':
        data['转发'] = '0'
    else:
        data['转发'] = zhuan
    data['时间'] = time
    return data

#这里限制一下微博的发布时间
a = "2019-12-01"
timeArray = time.strptime(a, "%Y-%m-%d")
stop_time = int(time.mktime(timeArray))

def time_case(case):
    if len(case) == 10:
        timeArray = time.strptime(case, "%Y-%m-%d")
        timeStamp = int(time.mktime(timeArray))
        if timeStamp < stop_time:
            return 0
        else:
            return 1
    else:
        return 1

def main(userID,out_path):
    url = 'https://m.weibo.cn/u/' + userID   
    driver = start_chrome(url)
    
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_str = {'start time':start_time}
    user_info = info_spider(driver)
    user_name = user_info['user_name']
    with open(out_path + '%s.json'%user_name, 'a+', encoding='utf-8') as f:
        f.write('[')
        json_time = json.dumps(time_str, ensure_ascii=False)
        f.write(json_time)
        f.write(',')
        json_user = json.dumps(user_info, ensure_ascii=False)
        f.write(json_user)
        f.write(',')
    
    temp = 0
    axis_time = '0'
    while time_case(axis_time) == 1:  

        weiboList = get_weiboList(driver)
        for weibo in weiboList[temp: ]:
            data = crwal_spider(driver, weibo)
            with open(out_path + '%s.json'%user_name, 'a+', encoding='utf-8') as f:
                json_str = json.dumps(data, ensure_ascii=False)
                f.write(json_str)
                f.write(',')

        temp = len(weiboList)
        axis_time = weiboList[-1].find_element_by_xpath('div//header//span[@class="time"]').text
        print(axis_time)
        
        counter = 0
        for i in range(5):
            counter += 1
            driver.find_element_by_tag_name('body').send_keys(Keys.END)
            time.sleep(2)
            print("当前微博数为%d" % len(get_weiboList(driver)))
            if temp != len(get_weiboList(driver)):
                  break
        if counter == 5:
            axis_time = "2019-01-01"
            
        if temp > 1000:
            axis_time = "2019-01-01"
    driver.close()

with open('new_userID.json', 'r') as f:
    IDList = json.loads(f.read())         #一共是4664个ID
List = IDList[0:500]     #这里改一下范围

out_path = 'data_1/'    #路径可改，先建立一下文件夹，抓取的用户文件全在该文件夹内
for user_id in List:
    try:
        main(user_id,out_path)
    except:
        pass
        
