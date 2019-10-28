# -*- encoding: utf8 -*-
import sys
import json
import time
import random
#from scrapy.http import request
import requests
import traceback
from datetime import datetime
from pprint import pprint



def start(interval=0, initialize=False):
    client = Crawler(interval=5)
    seed = "https://36kr.com/api/search-column/mainsite?per_page={per_page}&page={page}&_=1543840108547"
    new_articles = list()
    for r in client.request(seed):
        for i in r["data"]["items"]:
            if "is_free" not in i:
                continue
            new_articles.append("https://36kr.com/p/{}\n".format(i["id"]))
    with open("./dict/articles.txt", "a") as fp:
        fp.writelines(new_articles)


class Crawler(object):

    user_agent = list()

    def __init__(self, logger=None, interval=2):
        self.logger = logger
        self.interval = interval
        with open("./dict/user_agent.txt", "r") as fp:
            self.user_agent = fp.readlines()

    def request(self, seed):

        for p in range(1,10):
            try:
                url = seed.format(per_page=100, page=p)
                header = self._get_header()
                print("Start: {} {}".format(url, header))
                response = requests.get(
                    url,
                    header
                )
                print(response.content)
                if response.status_code/100 != 2:
                    raise Exception(response.reason)
                rt = json.loads(response.content)
                rt.update({
                    "record_time": datetime.now()
                })
                print("Finish: {} {}".format(url, header))
                yield rt
            except Exception as e:
                print("Fetch error", traceback.format_exc(), sys.stderr)
                raise
            break
            time.sleep(self.interval)


    def _get_header(self):
        header = {
            # 伪造下UA
            "User-Agent": random.choice(self.user_agent),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            # 伪造下Referer
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4",
            "Content-Type": "application/json; charset=utf-8"
        }
        header = {
            "Upgrade-Insecure-Requests": 1,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3"
        }


        return header


    def _detail_new_book(self):
        # zoneXX 循环
        # 根据地标来搞，地标再分用户类型 holiday or business
        # zone_list:  url = "http://hotels.ctrip.com/domestic-1.html"
        for zone in self.zone_dict:
            self.logger.info("Zone: %s %s" % (zone, self.zone_dict[zone]))
            url = "http://hotels.ctrip.com/hotel/beijing1/{}".format(zone)
            header = self._get_header()

            time.sleep(random.choice(range(0,3)))
            yield (url, header, zone)

if __name__ == "__main__":
    start()
