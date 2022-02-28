# Name: Multi information clock main
# Author: marksard
# Version: 2.0
# Python 3.6 or later (maybe)

# ***************************
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QPushButton, QSizePolicy
from pytz import timezone
from subprocess import Popen, PIPE

import datetime
import os
import psutil
import sys
import threading
import json
import traceback
import pandas as pd
# import weatherinfo as forecast

# ***************************
USE_SPDTST = True
USE_BME = True
USE_WEATHER = True

if os.name != 'nt':
    import pwd
else:
    USE_SPDTST = False
    USE_BME = False
    USE_WEATHER = True

if USE_BME == True:
    import bme280

if USE_WEATHER == True:
    import weather_tenkijp as forecast

# ***************************
class QCustomLabel(QLabel):
    def __init__(self, text: str) -> None:
        super(QCustomLabel, self).__init__(text)
        self.font = QFont("Let's go Digital", 11)
        # self.font = QFont('Source Han Code JP Medium', 11)
        # self.font = QFont("Capsuula", 11)
        self.font.insertSubstitutions('Source Han Code JP Medium', [
                                      'Source Han Code JP N', '源ノ角ゴシック Code JP M', '源ノ角ゴシック Code JP N'])
        self.setFont(self.font)
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.setContentsMargins(-3, -1, -3, -1)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.fontScale = 1.0
        self.callback = None

    def set_font_family(self, face) -> None:
        self.font.setFamily(face)

    def set_font_scale(self, scale) -> None:
        self.fontScale = scale

    def resizeEvent(self, evt):
        width = self.size().width() / len(self.text())
        height = self.size().height()
        baseSize = 0
        if width > height:
            baseSize = height
        else:
            baseSize = width

        self.font.setPixelSize(baseSize * self.fontScale)
        self.setFont(self.font)

        if self.callback is not None:
            self.callback(self.size().width(), self.size().height())
    
    def set_callback(self, callback):
        self.callback = callback

# ***************************
# 色変え用
class QCustomLabel2(QCustomLabel):
    def __init__(self, text: str) -> None:
        super(QCustomLabel2, self).__init__(text)


# ***************************
class ClockDisplay:
    # Convert from OpenWetherMap weather ID to Meteocons weather icon.
    # weather ID 200/300/500/600 convert to 2/3/5/6
    WEATHER_ICON = {
        2: 'P', # 雷
        3: 'X', # みぞれ
        5: 'R', # 雨
        6: 'W', # 雪
        800: 'B', # 晴れ
        801: 'B',
        802: 'H', # 晴れ時々曇り
        803: 'N', # 曇り
        804: 'Y', # 雲
    }

    WEATHER_ICON_MOON = {
        800: 'C', # 晴れ
        801: 'C',
        802: 'I', # 晴れ時々曇り
    }

    WEEK_NAMES = ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']

    def __init__(self) -> None:
        self.__app = QApplication(sys.argv)
        self.__window = QWidget()
        self.__layout = QGridLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setHorizontalSpacing(2)
        self.__layout.setVerticalSpacing(2)

        self.__labelDate = QCustomLabel('initializing')
        self.__labelTimes = []
        self.__labelForecastTimes = []
        self.__labelForecastWeathers = []
        self.__labelForecastTemps = []
        self.__labelForecastRains = []
        self.__labelForecastWinds = []
        self.__labelTemperature = QCustomLabel('  ')
        self.__labelHumidity = QCustomLabel('  ')
        self.__labelPressure = QCustomLabel('   ')
        self.__labelUpload = QCustomLabel(' ')
        self.__labelDownload = QCustomLabel(' ')
        self.__labelPing = QCustomLabel(' ')

        # self.__labelForecastWindsUnit = QCustomLabel2('m/s')
        self.__labelForecastRainsUnit = QCustomLabel2('mm')
        self.__labelForecastTempsUnit = QCustomLabel2("'C")
        self.__labelTemperatureUnit = QCustomLabel2("'C")
        self.__labelHumidityUnit = QCustomLabel2(' %')
        self.__labelPressureUnit = QCustomLabel2('hPa')

        self.__labelUploadUnit = QCustomLabel2('Down\n(Mbps)')
        self.__labelDownloadUnit = QCustomLabel2('Up\n(Mbps)')
        self.__labelPingUnit = QCustomLabel2('Ping\n(ms)')

        self.__last_time = datetime.datetime.min

        self.__fullMode = False

        self.__valTemperature = 0
        self.__valHumidity = 0
        self.__valPressure = 0
        self.__valUpload = 0
        self.__valDownload = 0
        self.__valPing = 0

        self.__weathers_cache = None

        self.__sphere = None
        if USE_BME == True:
            self.__sphere = bme280.BME280()
            self.__sphere.initialize()

        self.__set_style()
        self.__initialize_display_items()
        self.__initialize_display_items_scale()
        self.__initialize_display_layout()

    def start(self) -> None:
        timer = QTimer()
        timer.timeout.connect(self.__on_timer)
        timer.start(200)

        self.__window.setLayout(self.__layout)
        self.__window.resize(300, 200)
        self.__window.show()

        self.__update_weather(use_cache=False)
        self.__update_speed_test()
        self.__update_room_info()

        sys.exit(self.__app.exec_())

    def __set_style(self) -> None:
        styleNight = """
            QWidget{background-color:#03161B;} 
            .QCustomLabel{color:#83FDF4; background-color:#073642;}
            .QCustomLabel2, QPushButton{color:#7f83FDF4; background-color:#7f073642;}
        """
        self.__app.setStyleSheet(styleNight)
        # styleNight = 'QWidget{background-color:#407b8e72;} QLabel, QPushButton{color:#DCF7C9; background-color:#111111;}'
        # self.__app.setStyleSheet(styleNight)

    def __initialize_display_items(self) -> None:
        initTimes = ['  ', ':', '  ', ':','  ']
        for item in initTimes:
            if item == ':':
                self.__labelTimes.append(QCustomLabel2(item))
            else:
                self.__labelTimes.append(QCustomLabel(item))

        for i in range(8):
            self.__labelForecastTimes.append(QCustomLabel2(' '))
            self.__labelForecastWeathers.append(QCustomLabel(' '))
            self.__labelForecastTemps.append(QCustomLabel(' '))
            self.__labelForecastRains.append(QCustomLabel(' '))
            self.__labelForecastWinds.append(QCustomLabel(' '))

    def __initialize_display_items_scale(self) -> None:
        self.__labelDate.set_font_scale(1.7)

        for i in range(len(self.__labelTimes)):
            self.__labelTimes[i].set_font_scale(1.7)
        # self.__labelTimes[3].setAlignment(
        #     QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        for i in range(len(self.__labelForecastTimes)):
            self.__labelForecastWinds[i].set_font_scale(1.8)
            self.__labelForecastRains[i].set_font_scale(1.4)
            self.__labelForecastTemps[i].set_font_scale(1.4)
            self.__labelForecastTimes[i].set_font_scale(1.4)
            self.__labelForecastWeathers[i].set_font_family('Meteocons')

        # self.__labelForecastWindsUnit.set_font_scale(1.0)
        self.__labelForecastRainsUnit.set_font_scale(1.0)
        self.__labelForecastTempsUnit.set_font_scale(1.0)

        self.__labelTemperature.set_font_scale(1.3)
        self.__labelHumidity.set_font_scale(0.8)
        self.__labelPressure.set_font_scale(1.4)

        self.__labelTemperatureUnit.set_font_scale(1.0)
        self.__labelHumidityUnit.set_font_scale(1.0)
        self.__labelPressureUnit.set_font_scale(1.2)

        self.__labelUpload.set_font_scale(1)
        self.__labelUploadUnit.set_font_scale(1.8)
        self.__labelDownload.set_font_scale(1)
        self.__labelDownloadUnit.set_font_scale(1.8)
        self.__labelPing.set_font_scale(1)
        self.__labelPingUnit.set_font_scale(1.8)

    def __initialize_display_layout(self) -> None:
        # addWidget(obj, row-pos, col-pos, row-span, col-span)
        self.__layout.addWidget(self.__labelDate, 0, 0, 1, 8)

        self.__layout.addWidget(self.__labelTimes[0], 1, 0, 2, 2)
        self.__layout.addWidget(self.__labelTimes[1], 1, 2, 2, 1)
        self.__layout.addWidget(self.__labelTimes[2], 1, 3, 2, 2)
        self.__layout.addWidget(self.__labelTimes[3], 1, 5, 2, 1)
        self.__layout.addWidget(self.__labelTimes[4], 1, 6, 2, 2)

        for i in range(len(self.__labelForecastTimes)):
            self.__layout.addWidget(self.__labelForecastWinds[i], 0, i + 9)
            self.__layout.addWidget(self.__labelForecastRains[i], 1, i + 9)
            self.__layout.addWidget(self.__labelForecastTemps[i], 2, i + 9)
            self.__layout.addWidget(self.__labelForecastTimes[i], 3, i + 9)
            self.__layout.addWidget(self.__labelForecastWeathers[i], 4, i + 9)

        # self.__layout.addWidget(self.__labelForecastWindsUnit, 0, 8)
        self.__layout.addWidget(self.__labelForecastRainsUnit, 1, 8)
        self.__layout.addWidget(self.__labelForecastTempsUnit, 2, 8)

        self.__layout.addWidget(self.__labelTemperature, 3, 0, 1, 2)
        self.__layout.addWidget(self.__labelTemperatureUnit, 3, 2)
        self.__layout.addWidget(self.__labelHumidity, 3, 3, 1, 2)
        self.__layout.addWidget(self.__labelHumidityUnit, 3, 5)
        self.__layout.addWidget(self.__labelPressure, 3, 6, 1, 2)
        self.__layout.addWidget(self.__labelPressureUnit, 3, 8)

        self.__layout.addWidget(self.__labelUpload, 4, 0, 1, 2)
        self.__layout.addWidget(self.__labelUploadUnit, 4, 2)
        self.__layout.addWidget(self.__labelDownload, 4, 3, 1, 2)
        self.__layout.addWidget(self.__labelDownloadUnit, 4, 5)
        self.__layout.addWidget(self.__labelPing, 4, 6, 1, 2)
        self.__layout.addWidget(self.__labelPingUnit, 4, 8)

        # Full screen change button
        screenChangeButton = QPushButton('km/h')
        screenChangeButton.clicked.connect(self.__on_click)
        screenChangeButton.setFont(QFont("Let's go Digital", 30))

        # QButtonはレイアウトによるストレッチができなさそうなので近場の処理で無理やりサイズを変更する
        def callback(w,h):
            screenChangeButton.setMinimumWidth(w)
            screenChangeButton.setMinimumHeight(h)
        self.__labelForecastTempsUnit.set_callback(callback)
        # self.__layout.addWidget(screenChangeButton, 4, 15, 1, 1)
        self.__layout.addWidget(screenChangeButton, 0, 8, 1, 1)

    def __update_clock(self, now: datetime.datetime) -> None:
        week = self.WEEK_NAMES[now.weekday()]
        self.__labelDate.setText(f'{now.strftime("%Y / %m / %d")}  {week}')
        self.__labelTimes[0].setText(now.strftime('%H'))
        self.__labelTimes[2].setText(now.strftime('%M'))
        self.__labelTimes[4].setText(now.strftime('%S'))

    def __update_room_info(self) -> None:
        bmeStatuses = self.__sphere.get_status()
        self.__valTemperature = bmeStatuses[0]
        self.__valHumidity = bmeStatuses[1]
        self.__valPressure = bmeStatuses[2]
        self.__labelTemperature.setText(self.__valTemperature)
        self.__labelHumidity.setText(self.__valHumidity)
        self.__labelPressure.setText(self.__valPressure)

    def __update_weather(self, use_cache = False) -> None:
        if self.__weathers_cache is None:
            if os.path.exists('weather_cache.csv'):
                print(f'Cache use: {datetime.datetime.now()}')
                cache = pd.read_csv('weather_cache.csv')
                cache['hours'] = pd.to_datetime(cache['hours'])
                data_check = cache[cache['hours'] > datetime.datetime.now()]
                self.__weathers_cache = cache
                if len(data_check) < 7:
                    print(f'Cache is old. Get it from web: {datetime.datetime.now()}')
                    self.__weathers_cache = forecast.get_weather_forecast()
                    self.__weathers_cache.set_index('hours').to_csv('weather_cache.csv')
            else:
                print(f'Cache is nothing. Get it from web: {datetime.datetime.now()}')
                self.__weathers_cache = forecast.get_weather_forecast()
                self.__weathers_cache.set_index('hours').to_csv('weather_cache.csv')
        elif use_cache == False:
            print(f'Get it from web: {datetime.datetime.now()}')
            self.__weathers_cache = forecast.get_weather_forecast()
            self.__weathers_cache.set_index('hours').to_csv('weather_cache.csv')

        weathers = self.__weathers_cache.copy()
        # 現時刻より前の過去データは除外
        weathers = weathers[weathers['hours'] > datetime.datetime.now() - datetime.timedelta(hours=3)]
        for i in range(len(self.__labelForecastTimes)):
            if len(weathers) <= i:
                break

            hour = weathers['hours'].iloc[i].hour
            self.__labelForecastTimes[i].setText("{0:2d}".format(hour))

            if hour < 6 or hour >= 18:
                style = 'background-color:#40073642;'
                self.__labelForecastWeathers[i].setStyleSheet(style)
                self.__labelForecastTemps[i].setStyleSheet(style)
                self.__labelForecastRains[i].setStyleSheet(style)
                self.__labelForecastWinds[i].setStyleSheet(style)
            else:
                style = 'background-color:#073642;'
                self.__labelForecastWeathers[i].setStyleSheet(style)
                self.__labelForecastTemps[i].setStyleSheet(style)
                self.__labelForecastRains[i].setStyleSheet(style)
                self.__labelForecastWinds[i].setStyleSheet(style)

            weatherId = weathers['condition_ids'].iloc[i]
            weatherIdOther = int(weatherId / 100)
            icons = self.WEATHER_ICON
            if (hour < 6 or hour >= 18) and weatherId in self.WEATHER_ICON_MOON:
                icons = self.WEATHER_ICON_MOON

            if weatherId in icons:
                self.__labelForecastWeathers[i].setText(icons[weatherId])
            elif weatherIdOther in icons:
                self.__labelForecastWeathers[i].setText(
                    icons[weatherIdOther])
            else:
                self.__labelForecastWeathers[i].setText('-')

            self.__labelForecastWeathers[i].resizeEvent(None)

            self.__labelForecastTemps[i].setText(
                '{:2.0f}'.format(weathers['temps'].iloc[i]))
            self.__labelForecastRains[i].setText(
                '{:2.0f}'.format(weathers['mm_rains'].iloc[i]))
            self.__labelForecastWinds[i].setText(
                '{:4.1f}'.format(weathers['winds'].iloc[i] * 3.6)) # m/s -> km/h
            
    def __update_speed_test(self) -> None:
        thread = threading.Thread(target=self.__update_speed_test_thread, name="updateSpeedTestThread")
        thread.start()

    def __update_speed_test_thread(self) -> None:
        try:
            for line in self.__execute_command('speedtest --format=json'):
                result = json.loads(line)
                if result is None:
                    return
                
                if 'upload' in result and 'bandwidth' in result['upload']:
                    self.__valUpload = result['upload']['bandwidth'] * 8 / 1000 / 1000
                    self.__labelUpload.setText('{:.1f}'.format(self.__valUpload))

                if 'download' in result and 'bandwidth' in result['download']:
                    self.__valDownload = result['download']['bandwidth'] * 8 / 1000 / 1000
                    self.__labelDownload.setText('{:.1f}'.format(self.__valDownload))

                if 'ping' in result and 'latency' in result['ping']:
                    self.__valPing = result['ping']['latency']
                    self.__labelPing.setText('{:.1f}'.format(self.__valPing))

            # print('upload:{0:.2f} download:{1:.2f} ping:{2:.2f}'.format(self.__valUpload, self.__valDownload, self.__valPing))
        except Exception as e:
            print(traceback.format_exc())

    def __execute_command(self, cmd) -> list:
        p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        out = out.decode('utf-8')
        return [s for s in out.split('\n') if s]

    def __on_click(self) -> None:
        if self.__fullMode == True:
            self.__fullMode = False
            self.__window.showNormal()
        else:
            self.__fullMode = True
            self.__window.showFullScreen()

    def __on_timer(self) -> None:
        now = datetime.datetime.now()
        if now.second == self.__last_time.second:
            return

        self.__last_time = now

        # 毎秒時刻更新
        self.__update_clock(now)

        # 10秒ごとに室温情報更新
        if now.second % 10 == 0:
            if USE_BME == True:
                self.__update_room_info()

        # 30分ごとにネット速度チェックして更新
        if (now.minute in [25, 55]) and now.second == 0:
            if USE_SPDTST == True:
                self.__update_speed_test()
        
        # 予報データの取得は日に4回ネットから更新
        if (now.hour in [0, 6, 12, 18]) and now.minute == 5 and now.second == 0:
            if USE_WEATHER == True:
                self.__update_weather(use_cache=False)

        # それ以外は3時間ごとにキャッシュデータを使って更新
        elif (now.hour % 3 == 0) and now.minute == 0 and now.second == 0:
            self.__update_weather(use_cache=True)

# ***************************
if __name__ == '__main__':
    clock = ClockDisplay()
    clock.start()
