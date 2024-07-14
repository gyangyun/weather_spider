import scrapy
from scrapy.shell import inspect_response

from tianqi.items import WeatherForecastItem
from tianqi.spiders.tq_utills import get_date_list, split_date_list
import demjson3

class TqybSpider(scrapy.Spider):
    name = 'tqyb'
    allowed_domains = ['j.i8tq.com', 'www.weather.com.cn', 'd1.weather.com.cn']
    start_urls = ['https://j.i8tq.com/weather2020/search/city.js']

    def parse(self, response):
        """
        城市对应城市编码解析
        """
        #  inspect_response(response, self)
        start_date = getattr(self, 'start_date', '202201')
        end_date = getattr(self, 'end_date', '202201')
        date_l = get_date_list(start_date, end_date)
        _, date_l = split_date_list(date_l)

        city_data = demjson3.decode(response.text[len('var city_data ='):])
        for province, city_d in city_data.items():
            if province not in ('广东', '广西', '云南', '贵州', '海南'):
                continue
            for city, county_d in city_d.items():
                code = county_d[city]['AREAID']
                for api_date in date_l:
                    api_url = 'http://d1.weather.com.cn/calendar_new/{}/{}_{}.html'.format(api_date[:4], code, api_date)

                    headers = {
                        'Referer': 'http://www.weather.com.cn/',
                    }
                    request = response.follow(api_url, self.parse_weather, headers=headers)
                    request.meta['province'] = province
                    request.meta['city'] = city
                    request.meta['code'] = code
                    yield request


    def parse_weather(self, response):
        """解析40天的天气预报数据
        {
            'date': '日期',
            'nlyf': '农历月份',
            'nl': '农历日期',
            'w1': '天气',
            'wd1': '风向',
            'max': '最高温度',
            'min': '最低温度',
            'jq': '节气',
            't1': '温度变化',
            'hmax': '历史最高温均值',
            'hmin': '历史最低温均值',
            'hgl': '历史降雨率',
            'alins': '黄历宜',
            'als': '黄历忌',
            }
        """
        #  inspect_response(response, self)
        tqinfo_list = demjson3.decode(response.text[len('var fc40 = '):])
        keys = ['date', 'nlyf', 'nl', 'w1', 'wd1', 'max', 'min', 'jq', 't1', 'hmax', 'hmin', 'hgl', 'alins', 'als']

        for tqinfo in tqinfo_list:
            if tqinfo['date']:
                #  data = WeatherForecastItem()
                data = {}
                data['province'] = response.meta['province']
                data['city'] = response.meta['city']
                data['city_code'] = response.meta['code']
                for key in keys:
                    data[key] = tqinfo[key]

                yield data
