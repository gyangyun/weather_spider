# -*- coding: utf-8 -*-
import re
from copy import deepcopy

import demjson3
import scrapy
from scrapy.shell import inspect_response

#  from scrapy_redis.spiders import RedisSpider



#  class TqSpider(RedisSpider):
class Tqyb15dSpider(scrapy.Spider):
    name = "tqyb15d"
    allowed_domains = ["tianqi.2345.com"]
    start_urls = ["http://tianqi.2345.com/js/citySelectData2.js"]

    def parse(self, response):
        """
        城市对应城市编码解析
        """
        # inspect_response(response, self)
        city_select_data = re.findall(
            r"var prov=new Array.*?台湾-36\'.*?(.*?)var provqx",
            response.body.decode("gbk"),
            re.S,
        )[0]
        #  解析出省份信息以及其对应的城市信息
        city_select_data_list = re.findall(
            "prov\[(\d+)\]\s?=\s?'(.*?)'", city_select_data, re.S
        )
        #  构建province --> city --> code 字典
        province_d = {}
        for province_code, city_s in city_select_data_list:
            try:
                city_d = {}
                for city_info in city_s.split("|"):
                    city_code_data = city_info.split(" ")[1]
                    city = city_code_data.split("-")[0]
                    city_code = city_code_data.split("-")[1]
                    city_d[city] = city_code
                province_d[int(province_code)] = city_d
            except Exception:
                continue
        #  只需要南方五省的数据
        province_code_d = {
            15: "广东",
            16: "广西",
            17: "贵州",
            18: "海南",
            41: "云南",
        }
        province_d = {
            f"{province_code_d[province_code]}-{province_code}": city_d
            for province_code, city_d in province_d.items()
            if province_code in province_code_d
        }
        for province_info, city_d in province_d.items():
            province, province_code = province_info.split("-")
            for city, city_code in city_d.items():
                cookies = {
                    # 'Hm_lvt_a3f2879f6b3620a363bec646b7a8bcdd': '1691029129',
                    # 'Hm_lpvt_a3f2879f6b3620a363bec646b7a8bcdd': '1691030977',
                    "lastCountyId": city_code,
                    # 'lastCountyTime': '1691031444',
                    # 'lastCountyPinyin': 'shenzhen',
                    "lastCityId": city_code,
                    "lastProvinceId": province_code,
                }
                headers = {
                    "authority": "tianqi.2345.com",
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                    "x-requested-with": "XMLHttpRequest",
                }
                api_url = "https://tianqi.2345.com/Pc/apiGet15Days"
                request = response.follow(
                    api_url,
                    cookies=cookies,
                    headers=headers,
                    dont_filter=True,
                    callback=self.parse_weather,
                )
                request.meta["province"] = province
                request.meta["province_code"] = province_code
                request.meta["city"] = city
                request.meta["city_code"] = city_code
                # self.log(cookies)
                yield request

    def parse_weather(self, response):
        """
        解析每月份天气数据
        :param response:
        :return:
        """
        # inspect_response(response, self)
        data = {}
        data["province"] = response.meta["province"]
        data["province_code"] = response.meta["province_code"]
        data["city"] = response.meta["city"]
        data["city_code"] = response.meta["city_code"]
        tqinfo_list = response.json().get("data", [])
        for tqinfo in tqinfo_list:
            tmp_data = deepcopy(data)
            tmp_data.update(tqinfo)
            yield tmp_data
