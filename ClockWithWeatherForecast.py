#! /usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QPushButton, QSizePolicy

import sys
import datetime
import weatherinfo

USE_BME = True

if USE_BME == True:
    from bme280 import bme280


class QCustomLabel(QLabel):
    def __init__(self, text):
        super(QCustomLabel, self).__init__(text)
        self.font = QFont('Source Han Code JP Medium', 11)
        self.font.insertSubstitutions('Source Han Code JP Medium', [
                                      'Source Han Code JP N', '源ノ角ゴシック Code JP M', '源ノ角ゴシック Code JP N'])
        self.setFont(self.font)
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.setContentsMargins(-3, -3, -3, -3)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.fontScale = 1.0

    def setFontFamily(self, face):
        self.font.setFamily(face)

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

    def __init__(self, app, window):
        self._app = app
        self._window = window
        self._labelDate = QCustomLabel('initializing')
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

        self.setNightMode()
        self.__initializeDisplayItems()
        self.__initializeDisplayItemsScale()
        self.__initializeDisplayLayout(layout)

    def __initializeDisplayItems(self):
        initTimes = ['  ', ':', '  ', '  ']
        for i in range(0, 4):
            self._labelTimes.append(QCustomLabel(initTimes[i]))

        for i in range(0, 7):
            self._labelForecastTimes.append(QCustomLabel(' '))
            self._labelForecastWeathers.append(QCustomLabel(' '))
            self._labelForecastTemps.append(QCustomLabel(' '))
            self._labelForecastRains.append(QCustomLabel(' '))

    def __initializeDisplayItemsScale(self):
        self._labelDate.setFontScale(1.1)

        for i in range(0, 4):
            self._labelTimes[i].setFontScale(1.1)
        self._labelTimes[3].setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        for i in range(0, 7):
            self._labelForecastTimes[i].setFontScale(0.5)
            self._labelForecastWeathers[i].setFontFamily('Meteocons')
            self._labelForecastTemps[i].setFontScale(0.9)
            self._labelForecastRains[i].setFontScale(0.8)

        self._labelForecastTimesUnit.setFontScale(0.8)
        self._labelForecastWeathersUnit.setFontScale(0.8)
        self._labelForecastTempsUnit.setFontScale(0.8)
        self._labelForecastRainsUnit.setFontScale(0.8)

    def __initializeDisplayLayout(self, layout):
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

    def updateClock(self, now):
        self._labelDate.setText(now.strftime('%Y/%m/%d %a'))
        self._labelTimes[0].setText(now.strftime('%H'))
        self._labelTimes[2].setText(now.strftime('%M'))
        self._labelTimes[3].setText(now.strftime('%S'))

    def updateRoomInfo(self):
        if USE_BME == True:
            bmeStatuses = self._bme.getStatus()
            self._labelTemperature.setText(bmeStatuses[0])
            self._labelHumidity.setText(bmeStatuses[1])
            self._labelPressure.setText(bmeStatuses[2])

    def updateWeather(self):
        weathers = weatherinfo.getWeatherForecast()
        for i in range(0, 7):
            if len(weathers) <= i:
                break

            hour = weathers[i][0].hour
            self._labelForecastTimes[i].setNum(hour)

            weatherId = weathers[i][1]
            weatherIdOther = int(weatherId / 100)
            icons = ClockDisplay.WEATHER_ICON
            if (hour < 6 or hour >= 18) and weatherId in ClockDisplay.WEATHER_ICON_MOON:
                icons = ClockDisplay.WEATHER_ICON_MOON

            if weatherId in icons:
                self._labelForecastWeathers[i].setText(icons[weatherId])
            elif weatherIdOther in icons:
                self._labelForecastWeathers[i].setText(
                    icons[weatherIdOther])
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

            self.updateClock(now)

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
                self.updateRoomInfo()

            if self._60SecCount == 0:
                self._60SecCount = 60
                # update_ntp_status_thread()

            if self._halfHourCount1 <= 0:
                self._halfHourCount1 = 1
                # update_speedtest_thread()
                print(now)
                self.updateWeather()

            if self._halfHourCount2 == 0:
                self._halfHourCount2 = 1
                # update_write_csv()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()

    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setHorizontalSpacing(1)
    layout.setVerticalSpacing(1)

    dispItems = ClockDisplay(app, window)

    timer = QTimer()
    timer.timeout.connect(dispItems.onTimer)
    timer.start(200)

    # now = datetime.datetime.today()
    # if now.hour >= 18:
    #     dispItems.setNightMode()
    # elif now.hour >= 6:
    #     dispItems.setDayMode()

    window.setLayout(layout)
    window.resize(300, 200)
    window.show()
    sys.exit(app.exec_())
