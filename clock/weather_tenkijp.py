import datetime
from tokenize import Ignore
import urllib3
from bs4 import BeautifulSoup
import pandas as pd

def get_weather_forecast():
    # 大阪市3時間ごとの天気
    url = 'https://tenki.jp/forecast/6/30/6200/27100/3hours.html'

    http = urllib3.PoolManager()
    instance = http.request('GET', url)
    soup = BeautifulSoup(instance.data, 'html.parser')

    # 今日と明日のデータを取得
    today = soup.select('#forecast-point-3h-today')
    w_today = __get_forecast_point_3h(today)
    tomorrow = soup.select('#forecast-point-3h-tomorrow')
    w_tommo = __get_forecast_point_3h(tomorrow)

    # datetime型に変換
    dt = datetime.datetime.now()
    w_today['hours'] = __hours_2_datetime(dt, w_today['hours'])
    dt = dt + datetime.timedelta(days=1)
    w_tommo['hours'] = __hours_2_datetime(dt, w_tommo['hours'])

    # openweathermapのcondition idにしたものを追加
    w_today['condition_ids'] = __weathers_2_condition_ids(w_today['weathers'])
    w_tommo['condition_ids'] = __weathers_2_condition_ids(w_tommo['weathers'])

    df = pd.DataFrame(w_today)
    df = df.append(pd.DataFrame(w_tommo))

    # 現時刻より前の過去データは除外
    df = df[df['hours'] > datetime.datetime.now()]

    result = []
    for index, item in df.iterrows():
        result.append([item['hours'], item['condition_ids'], item['temps'], item['mm_rains']])

    return result

def __get_forecast_point_3h(day):
    for item in day:
        data = item.select('tr.hour > td')
        hours = [v.getText(strip=True) for v in data]

        data = item.select('tr.weather > td')
        weathers = [v.getText(strip=True) for v in data]

        data = item.select('tr.temperature > td')
        temps = [float(v.getText(strip=True)) for v in data]

        data = item.select('tr.wind-speed > td')
        winds = [float(v.getText(strip=True)) for v in data]

        data = item.select('tr.prob-precip > td')
        perc_rains = [v.getText(strip=True) for v in data]

        data = item.select('tr.precipitation > td')
        mm_rains = [float(v.getText(strip=True)) for v in data]

    return {'hours':hours, 'weathers':weathers, 'temps':temps, 'winds':winds, 'perc_rains':perc_rains, 'mm_rains':mm_rains}

def __hours_2_datetime(dt, hours):
    result = []
    for i in range(len(hours)):
        hour_org = int(hours[i])
        hour = hour_org if hour_org < 24 else 0
        date = datetime.datetime(dt.year, dt.month, dt.day, hour, 0, 0, 0)
        date = date if hour_org < 24 else date + datetime.timedelta(days=1)
        result.append(date)

    return result

def __weathers_2_condition_ids(weathers):
    jp_2_owmid = {'晴':800, '曇':803, '雨':500, '雪':600, '雷':200, 'みぞれ':300}
    result = []
    for i in range(len(weathers)):
        weather = weathers[i]
        value = [v for k, v in jp_2_owmid.items() if k in weather]
        if len(value) == 0:
            value = [-1]
        result.append(value[0])

    return result

# ***************************
if __name__ == '__main__':
    result = get_weather_forecast()
    for item in result[0:7]:
        print(f'日時:{item[0]} 天気:{item[1]} 気温(℃):{item[2]} 雨量(mm):{item[3]:.2f}')
