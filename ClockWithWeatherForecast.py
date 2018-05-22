#! /usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QPushButton, QSizePolicy

import sys
import datetime
import weatherinfo

USE_BME = False

if USE_BME == True:
    from bme280 import bme280


class QCustomLabel(QLabel):
    def __init__(self, text):
        super(QCustomLabel, self).__init__(text)
        self.font = QFont('Source Han Code JP N', 11)
        self.setFont(self.font)
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.setContentsMargins(-3, -3, -3, -3)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.fontScale = 1.0

    def setFontScale(self, scale):
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


class ClockDisplay:
    WEATHER_ICON_DAY = {
        'clear sky': '☀',
        'few clouds': '☀☁',
        'scattered clouds': '☀☁',
        'broken clouds': '☁',
        'overcast clouds': '☁',
        'light rain': '☂',
        'moderate rain': '☔',
        'heavy intensity rain': '☔',
        'thunderstorm with light rain': '⚡☂',
        'thunderstorm with rain': '⚡☔',
        'thunderstorm with heavy rain': '⚡☔',
        'light snow': '☃',
        'snow': '☃',
        'heavy snow': '☃',
    }

    WEATHER_ICON_NIGHT = {
        'clear sky': '☽',
        'few clouds': '☽☁',
        'scattered clouds': '☽☁',
        'broken clouds': '☁',
        'overcast clouds': '☁',
        'light rain': '☂',
        'moderate rain': '☔',
        'heavy intensity rain': '☔',
        'thunderstorm with light rain': '⚡☂',
        'thunderstorm with rain': '⚡☔',
        'thunderstorm with heavy rain': '⚡☔',
        'light snow': '☃',
        'snow': '☃',
        'heavy snow': '☃',
    }

    def __init__(self, app, window):
        self._app = app
        self._window = window
        self._labelDate = QCustomLabel('initializing...')
        self._labelTimes = []
        self._labelForecastTimes = []
        self._labelForecastWeathers = []
        self._labelForecastTemps = []
        self._labelForecastRains = []
        self._labelTemperature = QCustomLabel('  ')
        self._labelHumidity = QCustomLabel('  ')
        self._labelPressure = QCustomLabel('   ')

        self._labelForecastTimesUnit = QCustomLabel('時')
        self._labelForecastWeathersUnit = QCustomLabel('天気')
        self._labelForecastTempsUnit = QCustomLabel('℃')
        self._labelForecastRainsUnit = QCustomLabel('mm')
        self._labelTemperatureUnit = QCustomLabel('℃')
        self._labelHumidityUnit = QCustomLabel('%')
        self._labelPressureUnit = QCustomLabel('hPa')

        self._1SecCount = 1
        self._10SecCount = 1
        self._60SecCount = 1
        self._halfHourCount1 = 0
        self._halfHourCount2 = 0
        self._fullMode = False
        self._bme = object

        if USE_BME == True:
            self._bme = bme280()
            self._bme.initialize()

    def initializeDisplayItems(self):
        initTimes = ['  ', ':', '  ', '  ']

        self._labelDate.setFontScale(1.1)

        for i in range(0, 4):
            self._labelTimes.append(QCustomLabel(initTimes[i]))
            self._labelTimes[-1].setFontScale(1.1)

        self._labelTimes[3].setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        for i in range(0, 7):
            self._labelForecastTimes.append(QCustomLabel(' '))
            self._labelForecastWeathers.append(QCustomLabel(' '))
            self._labelForecastTemps.append(QCustomLabel(' '))
            self._labelForecastRains.append(QCustomLabel(' '))
            self._labelForecastTimes[-1].setFontScale(0.5)
            self._labelForecastTemps[-1].setFontScale(0.9)
            self._labelForecastRains[-1].setFontScale(0.8)

        self._labelForecastTimesUnit.setFontScale(0.8)
        self._labelForecastWeathersUnit.setFontScale(0.8)
        self._labelForecastTempsUnit.setFontScale(0.8)
        self._labelForecastRainsUnit.setFontScale(0.8)

    def initializeDisplayLayout(self, layout):
        # addWidget(obj, row-pos, col-pos, row-span, col-span)
        layout.addWidget(self._labelDate, 0, 0, 1, 15)

        layout.addWidget(self._labelTimes[0], 1, 0, 3, 6)
        layout.addWidget(self._labelTimes[1], 1, 6, 3, 2)
        layout.addWidget(self._labelTimes[2], 1, 8, 3, 6)
        layout.addWidget(self._labelTimes[3], 1, 14, 3, 1)

        for i in range(0, 7):
            layout.addWidget(self._labelForecastTimes[i], 4, i * 2, 1, 2)
            layout.addWidget(self._labelForecastWeathers[i], 5, i * 2, 2, 2)
            layout.addWidget(self._labelForecastTemps[i], 7, i * 2, 1, 2)
            layout.addWidget(self._labelForecastRains[i], 8, i * 2, 1, 2)

        layout.addWidget(self._labelForecastTimesUnit, 4, 14)
        layout.addWidget(self._labelForecastWeathersUnit, 5, 14, 2, 1)
        layout.addWidget(self._labelForecastTempsUnit, 7, 14)
        layout.addWidget(self._labelForecastRainsUnit, 8, 14)

        layout.addWidget(self._labelTemperature, 1, 15, 2, 2)
        layout.addWidget(self._labelTemperatureUnit, 1, 17, 2, 1)
        layout.addWidget(self._labelHumidity, 3, 15, 2, 2)
        layout.addWidget(self._labelHumidityUnit, 3, 17, 2, 1)
        layout.addWidget(self._labelPressure, 5, 15, 2, 2)
        layout.addWidget(self._labelPressureUnit, 5, 17, 2, 1)

        # Full screen change button
        screenChangeButton = QPushButton()
        screenChangeButton.clicked.connect(self.changeScreenMode)
        layout.addWidget(screenChangeButton, 0, 15, 1, 3)

        # Fill empty grid
        layout.addWidget(QLabel(), 7, 15, 2, 3)

    def changeScreenMode(self):
        if self._fullMode == True:
            self._fullMode = False
            self._window.showNormal()
        else:
            self._fullMode = True
            self._window.showFullScreen()

    def setNightMode(self):
        styleNight = 'QWidget{background-color:#407b8e72;} QLabel, QPushButton{color:#DCF7C9; background-color:#262626;}'
        self._app.setStyleSheet(styleNight)

    # def setDayMode(self):
    #     styleDay = 'QWidget{background-color:#7b8e72;} QLabel, QPushButton{color:#262626; background-color:#F3F9F1;}'
    #     self._app.setStyleSheet(styleDay)

    def updateWeather(self):
        weathers = weatherinfo.getWeatherForecast()
        for i in range(0, 7):
            if len(weathers) > i:
                hour = weathers[i][0].hour
                icons = ClockDisplay.WEATHER_ICON_NIGHT
                if hour >= 6 and hour <= 15:
                    icons = ClockDisplay.WEATHER_ICON_DAY

                self._labelForecastTimes[i].setNum(hour)

                if weathers[i][1] in icons:
                    self._labelForecastWeathers[i].setText(
                        icons[weathers[i][1]])
                else:
                    self._labelForecastWeathers[i].setText('-')
                self._labelForecastWeathers[i].resizeEvent(None)

                self._labelForecastTemps[i].setText(
                    '{:.0f}'.format(weathers[i][2]))
                self._labelForecastRains[i].setText(
                    '{:.0f}'.format(weathers[i][3]))

    def onTimer(self):
        now = datetime.datetime.today()
        self._1SecCount -= 1
        if self._1SecCount == 0:
            self._1SecCount = 5     # 200ms timer / 5 count = 1sec
            self._10SecCount -= 1
            self._60SecCount -= 1

            self._labelDate.setText(now.strftime('%Y/%m/%d %a'))
            self._labelTimes[0].setText(now.strftime('%H'))
            self._labelTimes[2].setText(now.strftime('%M'))
            self._labelTimes[3].setText(now.strftime('%S'))

            if (now.minute == 25 or now.minute == 55) and self._60SecCount == 0:
                self._halfHourCount1 -= 1

            if (now.minute == 30 or now.minute == 0) and self._60SecCount == 0:
                self._halfHourCount2 -= 1

            # if now.hour == 6 and now.minute == 0 and now.second == 0:
            #     self.setDayMode()

            # if now.hour == 18 and now.minute == 0 and now.second == 0:
            #     self.setNightMode()

        if self._10SecCount == 0:
            self._10SecCount = 10
            if USE_BME == True:
                bmeStatuses = self._bme.getStatus()
                self._labelTemperature.setText(bmeStatuses[0])
                self._labelHumidity.setText(bmeStatuses[1])
                self._labelPressure.setText(bmeStatuses[2])

            # if sec60_count == 0:
            #     sec60_count = 60
            #     update_ntp_status_thread()

            if self._halfHourCount1 <= 0:
                self._halfHourCount1 = 1
                # update_speedtest_thread()
                self.updateWeather()

            # if _halfHourCount2 == 0:
            #     _halfHourCount2 = 1
            #     update_write_csv()

        # now = datetime.datetime.today()
        # self._labelDate.setText(now.strftime('%Y/%m/%d %a'))
        # self._labelTimes[0].setText(now.strftime('%H'))
        # self._labelTimes[2].setText(now.strftime('%M'))
        # self._labelTimes[3].setText(now.strftime('%S'))

        # if now.hour >= 18 and viewMode == False:
        #     self.viewMode = True
        #     setViewMode(True)
        # elif now.hour >= 6 and view == True:
        #     self.viewMode = False
        #     setViewMode(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()

    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setHorizontalSpacing(1)
    layout.setVerticalSpacing(1)

    dispItems = ClockDisplay(app, window)
    dispItems.initializeDisplayItems()
    dispItems.initializeDisplayLayout(layout)

    timer = QTimer()
    timer.timeout.connect(dispItems.onTimer)
    timer.start(200)

    # now = datetime.datetime.today()
    # if now.hour >= 18:
    #     dispItems.setNightMode()
    # elif now.hour >= 6:
    #     dispItems.setDayMode()
    dispItems.setNightMode()

    window.setLayout(layout)
    window.resize(300, 200)
    window.show()
    sys.exit(app.exec_())
