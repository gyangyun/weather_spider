# -*- coding: utf-8 -*-

import scrapy


class WeatherItem(scrapy.Item):
    table_name = 'weather'
    province = scrapy.Field()
    city = scrapy.Field()
    city_code = scrapy.Field()
    ymd = scrapy.Field()
    bWendu = scrapy.Field()
    yWendu = scrapy.Field()
    tianqi = scrapy.Field()
    fengxiang = scrapy.Field()
    fengli = scrapy.Field()
    aqi = scrapy.Field()
    aqiInfo = scrapy.Field()
    aqiLevel = scrapy.Field()


class WeatherForecastItem(scrapy.Item):
    table_name = 'weather_forecast'
    province = scrapy.Field()
    city = scrapy.Field()
    city_code = scrapy.Field()
    date = scrapy.Field()
    nlyf = scrapy.Field()
    nl = scrapy.Field()
    w1 = scrapy.Field()
    wd1 = scrapy.Field()
    max = scrapy.Field()
    min = scrapy.Field()
    jq = scrapy.Field()
    t1 = scrapy.Field()
    hmax = scrapy.Field()
    hmin = scrapy.Field()
    hgl = scrapy.Field()
    alins = scrapy.Field()
    als = scrapy.Field()
