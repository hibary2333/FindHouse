#!/usr/bin/python3
# -*- coding: utf-8 -*-
#configure
image_width = 30
model_path = 'train/LR.pickle'
import requests
from bs4 import BeautifulSoup
import json
import csv
import codecs
import zrocr
#从每个房间的详情页获取房间id
def get_id(room_url):
    url = room_url
    header = {
        'user-agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'}

    page = requests.get(url, headers=header)
    room_soup = BeautifulSoup(page.text, "lxml")
    room_id = room_soup.find('input',id="room_id").get('value')
    house_id = room_soup.find('input',id="house_id").get('value')
    return room_id,house_id

#获取价格信息
def room_price(room_id,house_id):
    room_price_header = {
        'user-agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'
    }
    room_price_url = "http://www.ziroom.com/detail/info?id={}&house_id={}".format(room_id,house_id)
    #获取房价信息
    room_price_page = requests.get(room_price_url, headers = room_price_header)
    #因为源代码是json格式,这里需要处理json信息,获取价格url
    price = json.loads(room_price_page.text)['data']['price']
    #循环处理每个数据,获得价格信息
    price_pos = price[2]
    #找到图片地址
    num_list = 'http:' + price[0]
    return zrocr.ocr(price_pos, num_list)

#生成一个csv文件
def write_csv(file_name, datas):#file_name为写入CSV文件的路径，datas为要写入数据列表
    file_csv = codecs.open(file_name,'a+','utf-8')
    writer = csv.writer(file_csv)
    writer.writerow(datas)
    print("写入成功")

#爬取本页房子的信息
def get_info_in_one_page(url,header):
    page = requests.get(url, headers=header)
    soup = BeautifulSoup(page.text, "lxml")
    ul = soup.find('ul',id='houseList')
    li_list = ul.select("li") #获取单个房子的信息,用一个list存储它们
    for li in li_list:
        address = li.select("h3")[0].text.strip() # 获取房间名称
        descripe = [elem.text for elem in li.select(".detail")[0].select('span')] #获取房间具体信息.
        room_url = "http:" + li.select("a")[0].get("href")#获取房间详情网址
        room_id,house_id = get_id(room_url)#从房间详情获取房间id
        rooms_price = room_price(room_id,house_id)#获取房间价格
        roomlist = [address,descripe[0],descripe[1],descripe[2],rooms_price]
        write_csv('home.csv',roomlist)
#获取所有房子的信息
url = "http://www.ziroom.com/z/nl/z2-x4-u3.html?qwd=%E8%9E%8D%E6%B3%BD%E5%98%89%E5%9B%AD"
header = {'user-agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'}
page = requests.get(url, headers=header)
soup = BeautifulSoup(page.text, "lxml")
#获取页数
pagenum = soup.find("span", class_="pagenum").text.split('/')[1]
print(pagenum)
for pages in range(int(pagenum)):
    get_info_in_one_page(url + '&p=' + str(pages+1), header)
