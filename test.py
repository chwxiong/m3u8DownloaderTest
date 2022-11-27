import datetime
import os
import random
import socket
import re
import time

import requests
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import ssl
import certifi
import bs4  # BeautifulSoup是一个可以从html或xml文件中提取数据的Python库
import socket
from selenium import webdriver
from tqdm import tqdm
import shutil
import threading

"""
#Needed import
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

element_to_click = driver.find_element_by_id('smartdot_form_Button_1')  #  It simulates javascripts click events
ActionChains(driver).move_to_element(element_to_click).click().perform()

#Recommend to sleep after click, adjust time
sleep(3)
"""

timeout = 20
socket.setdefaulttimeout(timeout)


def getMainPageLinks(url):
    # requests.packages.urllib3.disable_warnings()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/107.0.1418.56",
        "cookie": "__utmz=43220850.1661001536.1.1.utmcsr=t0713.wonderfulday27.live|utmccn=(referral)|utmcmd=referral|utmcct=/; 91username=b51dLql786AUII1vNZAQKenkkZIintO%2BtxBTSKAdbLKw6w; DUID=5e75GobixPWh8EoKkOuTHsyf0jkDXAMdcekmCQTMopJzf8OYcw; USERNAME=5815BWuJem2wcFTnV7YCSGAqiyNp7ZaM7m%2Fwob5O3kuIFg; EMAILVERIFIED=yes; school=336fjm7vBtDwiDAlEG%2FSVz1q0KSMWtA7h34GwfA; level=a7b2mZ2dY4KItdH6R7b%2FZuPeFNunci7qe7NJwoy5; CLIPSHARE=63a7e95920fdbecf4af3d76120127e23; __utma=43220850.1768617353.1661001536.1661597791.1669425697.3; __utmc=43220850"
    }
    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.content, 'html.parser')
    domain = '{}://{}'.format(urlparse(url).scheme, urlparse(url).netloc)
    try:
        links = soup.findAll('a', href=re.compile
        ('^(https)((?!' + urlparse(domain).netloc + ').)*$'))
        print(links)
    except AttributeError:
        return None
    except ValueError:
        return None
    finally:
        html.close()


def download_m3u8(url):
    # download_path = os.getcwd() + "\download"
    ts_file = url.split("/")[-2]
    base_path ="F:\\百度云\\迅雷"
    download_path = os.path.join(base_path, ts_file)
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    all_content = requests.get(url).text  # 获取M3U8的文件内容
    file_line = all_content.split("\n")  # 读取文件里的每一行
    # 通过判断文件头来确定是否是M3U8文件
    ts_url_list = []
    if file_line[0] != "#EXTM3U":
        raise BaseException(u"非M3U8的链接")
    else:
        unknow = True  # 用来判断是否找到了下载的地址
        for index, line in enumerate(file_line):
            if "EXTINF" in line:
                unknow = False
                # 拼出ts片段的URL,
                ts_url = url.rsplit("/", 1)[0] + "/" + file_line[index + 1]
                ts_url_list.append(ts_url)
        if unknow:
            raise BaseException("未找到对应的下载链接")
        else:
            print("下载完成")
            ts_files = os.listdir(download_path)
            save_path = base_path + "\\" + time_name(ts_file) + ".mp4"
            for ts in tqdm(ts_files, desc="合并为mp4文件中......"):
                cur_ts_file = download_path + "\\" + ts
                if os.path.exists(cur_ts_file):
                    with open(cur_ts_file, 'rb') as f1:
                        with open(save_path, 'ab') as f2:
                            f2.write(f1.read())
                else:
                    print("{} 丢失".format(ts))
            # shutil.rmtree(download_path)

def download_ts(ts_url, download_path):
    try:
        res = requests.get(ts_url)
        ts_file, m3u8_file = ts_url.split('/')[-1].split('.')[0], ts_url.split('/')[-2]
        n = int(ts_file.lstrip(m3u8_file))
        with open(download_path + "\\" + str(1000+n) + ".ts", 'ab') as f:
            f.write(res.content)
            f.flush()
    except:
        print("{} 请求失败".format(ts_url))


def time_name(file_num):
    day = datetime.date.today()
    file_name = str(day.year) + "_" + str(day.month) + "_" + str(day.day) + "_" + file_num
    return file_name


if __name__ == '__main__':
    url_test = "https://www.baidu.com/"
    url_youtube = "https://www.youtube.com/"
    url_month_hot = "https://f0727.wonderfulday29.live/v.php?category=md&viewtype=basic&page=2"
    url_recent_hot = "https://f0727.wonderfulday29.live/v.php?category=rf&viewtype=basic"
    url_main_page = "https://f0727.wonderfulday29.live"
    # links = getMainPageLinks(url_main_page)
    download_m3u8_url = "http://blog.luckly-mjw.cn/tool-show/m3u8-downloader/index.html?source="
    m3u8_url = "https://la2.killcovid2021.com/m3u8/733943/733943.m3u8"
    url = download_m3u8_url + m3u8_url

    download_m3u8(m3u8_url)

    # nums = ts_long(m3u8_url)
    # links = bsObj.find('div', {'class': 'col-xs-12 col-sm-4 col-md-3 col-lg-3'}).findAll('a')
    # print(links)
