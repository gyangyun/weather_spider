# -*- coding: utf-8 -*-
import re

import demjson3
import scrapy
#  from scrapy_redis.spiders import RedisSpider

from tianqi.items import WeatherItem
from tianqi.spiders.tq_utills import get_date_list, split_date_list

from scrapy.shell import inspect_response

#  class TqSpider(RedisSpider):
class TqSpider(scrapy.Spider):
    name = 'tq'
    allowed_domains = ['tianqi.2345.com']
    start_urls = ['http://tianqi.2345.com/js/citySelectData.js']

    def parse(self, response):
        '''
        城市对应城市编码解析
        '''
        city_select_data = re.findall(r'var prov=new Array.*?台湾-36\'.*?(.*?)var provqx',
                                      response.body.decode('gbk'), re.S)[0]
        #  解析出省份信息以及其对应的城市信息
        city_select_data_list = re.findall("prov\[(\d+)\]\s?=\s?'(.*?)'", city_select_data, re.S)
        #  构建province --> city --> code 字典
        province_d = {}
        for province_code, city_s in city_select_data_list:
            try:
                city_d = {}
                for city_info in city_s.split('|'):
                    city_code_data = city_info.split(' ')[1]
                    city = city_code_data.split('-')[0]
                    code = city_code_data.split('-')[1]
                    city_d[city] = code
                province_d[int(province_code)] = city_d
            except Exception:
                continue
        #  只需要南方五省的数据
        province_code_d = {
                15: '广东',
                16: '广西',
                17: '贵州',
                18: '海南',
                41: '云南',
                }
        province_d = {province_code_d[province_code]: city_d for province_code, city_d in province_d.items() if province_code in province_code_d}
        # 开始构造请求，2011-2016和2017-未来需要不同的构建方式
        # 2011-2016: http://tianqi.2345.com/t/wea_history/js/城市id_年月.js  其中年月格式为:年份+整数月份          比如 二零一零年一月份为：20111
        # 2017-未来：http://tianqi.2345.com/t/wea_history/js/年月/城市id_年月.js   其中 年月格式为 年份+带序号的月份 比如二零零七年一月份为：201701

        start_date = getattr(self, 'start_date', '2021-01')
        end_date = getattr(self, 'end_date', '2021-01')
        #  date_l = get_date_list('2019-08', '2021-03')
        #  date_l = get_date_list('2014-01', '2021-03')
        date_l = get_date_list(start_date, end_date)

        date_old_l = [date_str for date_str in date_l if int(date_str.split('-')[0]) < 2017]
        for province, city_d in province_d.items():
            for city, code in city_d.items():
                for date in date_old_l:
                    api_date_1 = str(date.split('-')[0]) + str(int(date.split('-')[1]))
                    api_1_url = 'http://tianqi.2345.com/t/wea_history/js/{}_{}.js'.format(code, api_date_1)
                    request = response.follow(api_1_url, self.parse_weather)
                    request.meta['province'] = province
                    request.meta['city'] = city
                    request.meta['code'] = code
                    yield request

        date_new_l = [date_str for date_str in date_l if int(date_str.split('-')[0]) >= 2017]
        _, date_new_l = split_date_list(date_new_l)
        for province, city_d in province_d.items():
            for city, code in city_d.items():
                for api_date_2 in date_new_l:
                    api_2_url = 'http://tianqi.2345.com/t/wea_history/js/{}/{}_{}.js'.format(api_date_2, code, api_date_2)
                    request = response.follow(api_2_url, self.parse_weather)
                    request.meta['province'] = province
                    request.meta['city'] = city
                    request.meta['code'] = code
                    yield request

    def parse_weather(self, response):
        '''
        解析每月份天气数据
        :param response:
        :return:
        '''
        #  data = WeatherItem()
        data = {}
        data['province'] = response.meta['province']
        data['city'] = response.meta['city']
        data['city_code'] = response.meta['code']
        weather = response.body.decode('gbk')[16:-1]
        #  inspect_response(response, self)
        weather_dict = demjson3.decode(weather)
        data['city'] = weather_dict.get('city')
        tqinfo_list = weather_dict.get('tqInfo')
        for tqinfo in tqinfo_list:
            if tqinfo:
                for key, value in tqinfo.items():
                    data[key] = value
                    if key == 'bWendu' or key == 'yWendu':
                        try:
                            data[key] = int(value[:-1])
                        except ValueError:
                            data[key] = ''
                yield data
