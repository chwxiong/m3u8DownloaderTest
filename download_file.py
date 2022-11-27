import datetime
import os
import random
import socket
import re
import time
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
from tqdm import tqdm
import shutil
import threading

base_path = "F:\\百度云\\迅雷\\download"
ts_nums_dic = {}
failed_url_queue = []
ts_url_queue = []


class GetTsLinks(threading.Thread):

    def __init__(self, m3u8_queue, ts_queue):
        super().__init__()
        self.url_m3u8_queue = m3u8_queue
        self.ts_url_queue = ts_queue

    def run(self) -> None:
        while True:
            if not self.url_m3u8_queue:
                break
            # print('当前线程的名字是： ', threading.current_thread().name)
            url_m3u8 = self.url_m3u8_queue.pop(0)
            print("开始处理{}, 还剩{}个m3u8链接未处理".format(url_m3u8, len(self.url_m3u8_queue)))
            get_ts_url(url_m3u8)


class DownloadTsFile(threading.Thread):
    def __init__(self, ts_queue):
        super().__init__()
        self.ts_url_queue = ts_queue

    def run(self) -> None:
        while True:
            if not self.ts_url_queue:
                break
            print('当前Ts线程的名字是： ', threading.current_thread().name)
            ts_url = self.ts_url_queue.pop(0)
            print("开始处理{}, 还剩{}个ts文件下载".format(ts_url, len(self.ts_url_queue)))
            download_ts(ts_url)


def get_ts_url(url_m3u8):
    m3u8_file = url_m3u8.split("/")[-2]
    download_path = os.path.join(base_path, m3u8_file)
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    time.sleep(random.randrange(1, 3))
    all_content = requests.get(url_m3u8).text  # 获取M3U8的文件内容
    file_line = all_content.split("\n")  # 读取文件里的每一行
    if file_line[0] != "#EXTM3U":
        raise BaseException(u"非M3U8的链接")
    else:
        unknow = True  # 用来判断是否找到了下载的地址
        num = 0
        for index, line in enumerate(file_line):
            if "EXTINF" in line:
                unknow = False
                ts_url = url_m3u8.rsplit("/", 1)[0] + "/" + file_line[index + 1]
                ts_url_queue.append(ts_url)
                num += 1
        ts_nums_dic[m3u8_file] = num
        print("{}共有{}个ts文件".format(m3u8_file, num))
        if unknow:
            raise BaseException("未找到对应ts的下载链接")


def download_ts(ts_url):
    try:
        time.sleep(random.randrange(1, 2))
        ts_file, m3u8_file = ts_url.split('/')[-1].split('.')[0], ts_url.split('/')[-2]
        download_path = os.path.join(base_path, m3u8_file)
        n = int(ts_file.lstrip(m3u8_file))
        if (str(1000 + n) + ".ts") not in os.listdir(download_path):
            res = requests.get(ts_url)
            with open(download_path + "\\" + str(1000 + n) + ".ts", 'ab') as f:
                f.write(res.content)
                f.flush()
    except:
        print("{} 请求失败".format(ts_url))
        failed_url_queue.append(ts_url)


def generate_mp4(m3u8_file):
    ts_path = os.path.join(base_path, m3u8_file)
    ts_num = len(os.listdir(ts_path))
    if ts_num / ts_nums_dic[m3u8_file] >= 0.9:
        ts_files = os.listdir(ts_path)
        save_path = "F:\\百度云\\迅雷" + "\\" + time_name(m3u8_file) + ".mp4"
        for ts in tqdm(ts_files, desc="合并为{}.mp4文件中......".format(m3u8_file)):
            cur_ts_file = ts_path + "\\" + ts
            if os.path.exists(cur_ts_file):
                with open(cur_ts_file, 'rb') as f1:
                    with open(save_path, 'ab') as f2:
                        f2.write(f1.read())
            else:
                print("{} 丢失".format(ts))
        # shutil.rmtree(download_path)
    else:
        print("{}下载失败ts文件过多，请重试!".format(m3u8_file))


def time_name(m3u8_file):
    day = datetime.date.today()
    file_name = str(day.year) + "_" + str(day.month) + "_" + str(day.day) + "_" + m3u8_file
    return file_name


if __name__ == '__main__':
    url_m3u8_queue, ts_url_queue, failed_url_queue = [], [], []
    with open("m3u8.txt", 'r') as f:
        for line in f.readlines():
            url_m3u8_queue.append(line.strip("\n"))
    start_time = time.time()
    threads = []
    for i in range(3):
        p = GetTsLinks(url_m3u8_queue, ts_url_queue)
        p.start()
        threads.append(p)
    time.sleep(10)
    for j in range(5):
        c = DownloadTsFile(ts_url_queue)
        c.start()
        threads.append(c)
    # print("活跃的线程个数：", threading.active_count())
    for t in threads:  # 等待所有线程完成
        t.join()
    end_time = time.time()
    print("总耗时：{:.2f}s".format(end_time - start_time))
    print("ts_nums_dic:", ts_nums_dic)
    for file in os.listdir(base_path):
        generate_mp4(file)
