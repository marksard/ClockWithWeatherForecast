#! /usr/bin/python3
# -*- coding: utf-8 -*-

import json
import datetime
import os
import requests
import sys

from pytz import timezone
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ.get("API_KEY")
API_URL = "http://API_URL.openweathermap.org/data/2.5/forecast?zip={zip}&units=metric&APPID={key}"

def getWeatherForecast():
    url = API_URL.format(zip = '537-0003,JP', key = API_KEY)
    response = requests.get(url)
    data = json.loads(response.text)

    result = []
    for entry in data['list']:
        w_datetime = datetime.datetime.utcfromtimestamp(entry['dt'])
        w_weather = entry['weather'][0]['main']
        w_weather_desc = entry['weather'][0]['description']
        w_temp = entry['main']['temp']
        w_rain = 0
        if 'rain' in entry and '3h' in entry['rain']:
            w_rain = entry['rain']['3h']
        result.append([w_datetime, w_weather, w_weather_desc, w_temp, w_rain])
        print('日時:{0} 天気:{1}({4}) 気温:{2} 雨量(mm):{3}'.format(w_datetime, w_weather, w_temp, w_rain, w_weather_desc))

    return result
