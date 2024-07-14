import os

if __name__ == '__main__':
    #  os.system("scrapy crawl tq")
    os.system("scrapy crawl tq -o csg_weather_202103_202105.csv -a start_date=2021-03 -a end_date=2021-05")
