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

load_dotenv(join(dirname(__file__), '.env'))

API_KEY = os.environ.get("API_KEY")
API_URL = "http://api.openweathermap.org/data/2.5/forecast?zip={zip}&units=metric&APPID={key}"


def getWeatherForecast():
    url = API_URL.format(zip='537-0003,JP', key=API_KEY)
    response = requests.get(url)
    forecastData = json.loads(response.text)

    result = []
    if not ('list' in forecastData):
        result.append([datetime.datetime.today(), 800, 40.2, 0.0])
        return result

    for item in forecastData['list']:
        forecastDatetime = timezone(
            'Asia/Tokyo').localize(datetime.datetime.fromtimestamp(item['dt']))
        weatherId = item['weather'][0]['id']
        weatherDescription = item['weather'][0]['description']
        temperature = item['main']['temp']
        rainfall = 0
        if 'rain' in item and '3h' in item['rain']:
            rainfall = item['rain']['3h']
        result.append(
            [forecastDatetime, weatherId, temperature, rainfall])
        print('日時:{0} 天気:({1}){2} 気温(℃):{3} 雨量(mm):{4}'.format(
            forecastDatetime, weatherId, weatherDescription, temperature, rainfall))

    return result

# getWeatherForecast()