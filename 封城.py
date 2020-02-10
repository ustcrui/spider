#!/usr/bin/env python
# coding: utf-8

# In[7]:


import selenium
import time
from tqdm import *
import json
import random
import time
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from apscheduler.schedulers.blocking import BlockingScheduler


# In[8]:


def get_weiboList(driver):
    retList = driver.find_element_by_xpath('/html[1]/body[1]/div[1]/div[1]/div[1]').find_elements_by_class_name('card9')
    return retList

def get_content(driver, path):
    js = 'window.open("%s")' % path
    driver.execute_script(js)
    driver.switch_to.window(driver.window_handles[1])
    text = driver.find_element_by_xpath('//div[@class="weibo-og"]').text
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return text

def start_chrome(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options = options) 
    driver.get(url)
    driver.implicitly_wait(5)     #所有页面隐性等待
    driver.find_element_by_xpath('//div[@class="scroll-box nav_item"]/ul/li[3]/span').click()
    return driver


# In[9]:


# 提取被转发微博的相关信息

def rp_weibo(driver, weibo):
    data = {}

    # 判断是否存在转发微博
    try:
        weibo.find_element_by_xpath('div//div[@class="weibo-rp"]')
    except:
        return None

    # 转发用户及时间
    nodeUser = []
    nodeText = []

    node_box = weibo.find_element_by_xpath('div//div[@class="weibo-og"]').text
    response_box = node_box.split('//@')

    for i in reversed(range(1, len(response_box))):
        infobox = response_box[i].split(':', 1)
        nodeUser.append(infobox[0])
        nodeText.append(infobox[1])

    nodeLen = len(nodeUser)
    responseNode = {}
    for i in range(nodeLen):
        node = {}
        node['用户名'] = nodeUser[i]
        node['转发内容'] = nodeText[i]
        responseNode['节点%d' % (i + 1)] = node

    lastUser = weibo.find_element_by_xpath('div//header/div//a').text
    lastTime = weibo.find_element_by_xpath('div//header//span[@class="time"]').text
    lastNode = {}
    lastNode['用户名'] = lastUser
    lastNode['转发内容'] = response_box[0]
    responseNode['节点%d' % (nodeLen + 1)] = lastNode

    # 被转发的原始微博
    user = weibo.find_element_by_xpath('div//div[@class="weibo-rp"]//div[@class="weibo-text"]/span[1]').text
    text = weibo.find_element_by_xpath('div//div[@class="weibo-rp"]//div[@class="weibo-text"]/span[2]').text

    data['用户'] = user.replace('@', '')
    if "...全文" in text:
        link = weibo.find_element_by_xpath(
            'div//div[@class="weibo-rp"]//div[@class="weibo-text"]/span[2]/a[last()]').get_attribute('href')
        data['正文'] = get_content(driver, link)
    else:
        data['正文'] = text
    data['时间'] = lastTime
    data['转发节点'] = responseNode

    return data


# In[10]:


def original_weibo(driver, weibo):
    # 判断是否被转发
    info = weibo.find_element_by_xpath('div//footer/div//h4').text
    if "转发" in info:
        return None

    # 判断是否存在转发微博
    try:
        weibo.find_element_by_xpath('div//div[@class="weibo-rp"]')
    except:
        data = {}
        user = weibo.find_element_by_xpath('div//header//h3').text
        time = weibo.find_element_by_xpath('div//header//span[@class="time"]').text
        data['用户名'] = user
        data['时间'] = time
        text = weibo.find_element_by_xpath('div//div[@class="weibo-og"]').text
        if "...全文" in text:
            href = weibo.find_element_by_xpath('div//div[@class="weibo-og"]/div[1]/a[last()]').get_attribute('href')
            content = get_content(driver, href)
            data['正文'] = content
        else:
            data['正文'] = text
        return data
    return None


# In[15]:


def main(step):
    url = 'https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D%E5%B0%81%E5%9F%8E'
    driver = start_chrome(url)
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time_str = {'strat rime':start_time}
    with open('FengCheng_%d.json'%step, 'a+', encoding='utf-8') as f:
        json_str = json.dumps(time_str, ensure_ascii=False)
        f.write(json_str)
        f.write(',')
    temp = 0
    axis_time = 0
    stop_time = 60
    while axis_time < stop_time:  

        weiboList = get_weiboList(driver)
        print(len(weiboList))

        for weibo in weiboList[temp: ]:
            if rp_weibo(driver, weibo) == None:
                if original_weibo(driver, weibo) == None:
                    continue
                else:
                    data = original_weibo(driver, weibo)
            else:
                data = rp_weibo(driver, weibo)
            with open('FengCheng_%d.json'%step, 'a+', encoding='utf-8') as f:
                json_str = json.dumps(data, ensure_ascii=False)
                f.write(json_str)
                f.write(',')

        temp = len(weiboList)
        weibo_time = weiboList[-1].find_element_by_xpath('div//header//span[@class="time"]').text
        print(temp, weibo_time)

        if '刚刚' in weibo_time:
            axis_time = 0
        if '1小时前' in weibo_time:
            axis_time = 60
        if '分钟' in weibo_time:
            axis_time = int(weibo_time.split('分钟')[0])

        for i in range(10):
            driver.find_element_by_tag_name('body').send_keys(Keys.END)
            time.sleep(2)
            print("当前微博数为%d" % len(get_weiboList(driver)))
            if temp != len(get_weiboList(driver)):
                  break
    driver.close()


# In[14]:


main(1)


# In[ ]:





# In[ ]:





# In[6]:


sched = BlockingScheduler()
sched.add_job(main(1), 'date', '2020-2-05 17:35:00')
sched.add_job(main(2), 'date', '2020-2-05 18:35:00')
sched.add_job(main(3), 'date', '2020-2-05 19:35:00')
sched.add_job(main(4), 'date', '2020-2-05 20:35:00')
sched.add_job(main(5), 'date', '2020-2-05 21:35:00')
sched.add_job(main(6), 'date', '2020-2-05 22:35:00')
sched.add_job(main(7), 'date', '2020-2-05 23:35:00')
sched.start()

