# Name: Multi information clock main
# Author: marksard
# Version: 2.0
# Python 3.6 or later (maybe)

# ***************************
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
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
import weatherinfo as weatherinfo

# ***************************
USE_CPUTEMP = True
USE_SPDTST = True
USE_BME = True
USE_WEATHER = True

if os.name != 'nt':
    import pwd
else:
    USE_CPUTEMP = False
    USE_SPDTST = False
    USE_BME = False
    USE_WEATHER = True

if USE_BME == True:
    import bme280

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

# ***************************
# 色変え用
class QCustomLabel2(QCustomLabel):
    def __init__(self, text: str) -> None:
        super(QCustomLabel2, self).__init__(text)


# ***************************
class ClockDisplay:
    # Convert from OpenWetherMap weather ID to Meteocons weather icon.
    WEATHER_ICON = {
        2: 'P',
        3: 'X',
        5: 'R',
        6: 'W',
        800: 'B',
        801: 'B',
        802: 'H',
        803: 'N',
        804: 'Y',
    }

    WEATHER_ICON_MOON = {
        800: 'C',
        801: 'C',
        802: 'I',
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
        self.__labelTemperature = QCustomLabel('  ')
        self.__labelHumidity = QCustomLabel('  ')
        self.__labelPressure = QCustomLabel('   ')
        self.__labelUpload = QCustomLabel(' ')
        self.__labelDownload = QCustomLabel(' ')
        self.__labelPing = QCustomLabel(' ')

        self.__labelForecastTimesUnit = QCustomLabel2(' ')
        self.__labelForecastWeathersUnit = QCustomLabel2(' ')
        self.__labelForecastTempsUnit = QCustomLabel2("'C")
        self.__labelForecastRainsUnit = QCustomLabel2('mm')
        self.__labelTemperatureUnit = QCustomLabel2("'C")
        self.__labelHumidityUnit = QCustomLabel2('%')
        self.__labelPressureUnit = QCustomLabel2('hPa')
        self.__labelUploadUnit = QCustomLabel2('U:Mbps')
        self.__labelDownloadUnit = QCustomLabel2('D:Mbps')
        self.__labelPingUnit = QCustomLabel2('ms')

        self.__last_time = datetime.datetime.min

        self.__fullMode = False

        self.__valTemperature = 0
        self.__valHumidity = 0
        self.__valPressure = 0
        self.__valUpload = 0
        self.__valDownload = 0
        self.__valPing = 0

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

        self.__update_weather()
        self.__update_speed_test()
        self.__update_room_info()

        sys.exit(self.__app.exec_())

    def __set_style(self) -> None:
        styleNight = 'QWidget{background-color:#03161B;} .QCustomLabel{color:#83FDF4; background-color:#073642;} .QCustomLabel2, QPushButton{color:#7f83FDF4; background-color:#7f073642;}'
        self.__app.setStyleSheet(styleNight)
        # styleNight = 'QWidget{background-color:#407b8e72;} QLabel, QPushButton{color:#DCF7C9; background-color:#111111;}'
        # self.__app.setStyleSheet(styleNight)

    def __initialize_display_items(self) -> None:
        initTimes = ['  ', ':', '  ', '  ']
        for item in initTimes:
            if item == ':':
                self.__labelTimes.append(QCustomLabel2(item))
            else:
                self.__labelTimes.append(QCustomLabel(item))

        for i in range(0, 7):
            self.__labelForecastTimes.append(QCustomLabel2(' '))
            self.__labelForecastWeathers.append(QCustomLabel(' '))
            self.__labelForecastTemps.append(QCustomLabel(' '))
            self.__labelForecastRains.append(QCustomLabel(' '))

    def __initialize_display_items_scale(self) -> None:
        self.__labelDate.set_font_scale(1.2)

        for i in range(len(self.__labelTimes)):
            self.__labelTimes[i].set_font_scale(1.5)
        self.__labelTimes[3].setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        for i in range(0, 7):
            self.__labelForecastTimes[i].set_font_scale(1.0)
            self.__labelForecastWeathers[i].set_font_family('Meteocons')
            self.__labelForecastTemps[i].set_font_scale(1.0)
            self.__labelForecastRains[i].set_font_scale(1.0)

        self.__labelForecastTimesUnit.set_font_scale(1.0)
        self.__labelForecastWeathersUnit.set_font_scale(1.0)
        self.__labelForecastTempsUnit.set_font_scale(1.0)
        self.__labelForecastRainsUnit.set_font_scale(1.0)

        self.__labelTemperature.set_font_scale(1.4)
        self.__labelHumidity.set_font_scale(1.4)
        self.__labelPressure.set_font_scale(1.4)

        self.__labelTemperatureUnit.set_font_scale(1.0)
        self.__labelHumidityUnit.set_font_scale(1.0)
        self.__labelPressureUnit.set_font_scale(1.0)

    def __initialize_display_layout(self) -> None:
        # addWidget(obj, row-pos, col-pos, row-span, col-span)
        self.__layout.addWidget(self.__labelDate, 0, 0, 2, 8)

        self.__layout.addWidget(self.__labelTimes[0], 2, 0, 4, 3)
        self.__layout.addWidget(self.__labelTimes[1], 2, 3, 4, 1)
        self.__layout.addWidget(self.__labelTimes[2], 2, 4, 4, 3)
        self.__layout.addWidget(self.__labelTimes[3], 2, 7, 4, 1)

        for i in range(0, 7):
            self.__layout.addWidget(self.__labelForecastTimes[i], 6, i)
            self.__layout.addWidget(self.__labelForecastWeathers[i], 7, i, 2, 1)
            self.__layout.addWidget(self.__labelForecastTemps[i], 9, i)
            self.__layout.addWidget(self.__labelForecastRains[i], 10, i)

        self.__layout.addWidget(self.__labelForecastTimesUnit, 6, 7)
        self.__layout.addWidget(self.__labelForecastWeathersUnit, 7, 7, 2, 1)
        self.__layout.addWidget(self.__labelForecastTempsUnit, 9, 7)
        self.__layout.addWidget(self.__labelForecastRainsUnit, 10, 7)

        self.__layout.addWidget(self.__labelTemperature, 2, 8, 2, 2)
        self.__layout.addWidget(self.__labelTemperatureUnit, 2, 10, 2, 1)
        self.__layout.addWidget(self.__labelHumidity, 4, 8, 2, 2)
        self.__layout.addWidget(self.__labelHumidityUnit, 4, 10, 2, 1)
        self.__layout.addWidget(self.__labelPressure, 6, 8, 2, 2)
        self.__layout.addWidget(self.__labelPressureUnit, 6, 10, 2, 1)

        self.__layout.addWidget(self.__labelUpload, 8, 8, 1, 2)
        self.__layout.addWidget(self.__labelUploadUnit, 8, 10, 1, 1)
        self.__layout.addWidget(self.__labelDownload, 9, 8, 1, 2)
        self.__layout.addWidget(self.__labelDownloadUnit, 9, 10, 1, 1)
        self.__layout.addWidget(self.__labelPing, 10, 8, 1, 2)
        self.__layout.addWidget(self.__labelPingUnit, 10, 10, 1, 1)

        # Full screen change button
        screenChangeButton = QPushButton()
        screenChangeButton.clicked.connect(self.__on_click)
        self.__layout.addWidget(screenChangeButton, 0, 10, 2, 1)

    def __update_clock(self, now: datetime.datetime) -> None:
        week = self.WEEK_NAMES[now.weekday()]
        self.__labelDate.setText(f'{now.strftime("%Y / %m / %d")}  {week}')
        self.__labelTimes[0].setText(now.strftime('%H'))
        self.__labelTimes[2].setText(now.strftime('%M'))
        self.__labelTimes[3].setText(now.strftime('%S'))

    def __update_room_info(self) -> None:
        if USE_BME == True:
            bmeStatuses = self.__sphere.get_status()
            self.__valTemperature = bmeStatuses[0]
            self.__valHumidity = bmeStatuses[1]
            self.__valPressure = bmeStatuses[2]
            self.__labelTemperature.setText(self.__valTemperature)
            self.__labelHumidity.setText(self.__valHumidity)
            self.__labelPressure.setText(self.__valPressure)

    def __update_weather(self) -> None:
        if USE_WEATHER == False:
            return

        weathers = weatherinfo.get_weather_forecast()
        for i in range(0, 7):
            if len(weathers) <= i:
                break

            hour = weathers[i][0].hour
            self.__labelForecastTimes[i].setText("{0:1d}".format(hour))

            weatherId = weathers[i][1]
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
                '{:.0f}'.format(weathers[i][2]))
            self.__labelForecastRains[i].setText(
                '{:.0f}'.format(weathers[i][3]))

    def __update_speed_test(self) -> None:
        if USE_SPDTST == True:
            thread = threading.Thread(target=self.__update_speed_test_thread, name="updateSpeedTestThread")
            thread.start()

    def __update_speed_test_thread(self) -> None:
        try:
            for line in self.__execute_command('speedtest --format=json'):
                result = json.loads(line)
                self.__valUpload = result['upload']['bandwidth'] * 8 / 1000 / 1000
                self.__valDownload = result['download']['bandwidth'] * 8 / 1000 / 1000
                self.__valPing = result['ping']['latency']

            # print('upload:{0:.2f} download:{1:.2f} ping:{2:.2f}'.format(self.__valUpload, self.__valDownload, self.__valPing))
            self.__labelUpload.setText('{:.1f}'.format(self.__valUpload))
            self.__labelDownload.setText('{:.1f}'.format(self.__valDownload))
            self.__labelPing.setText('{:.1f}'.format(self.__valPing))
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

        self.__update_clock(now)

        if (now.minute == 25 or now.minute == 55) and now.second == 0:
            self.__update_weather()
            self.__update_speed_test()

        if now.second % 10 == 0:
            self.__update_room_info()

# ***************************
if __name__ == '__main__':
    clock = ClockDisplay()
    clock.start()
