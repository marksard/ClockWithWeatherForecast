#! /usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QSizePolicy

import sys
import datetime

USE_BME = False

if USE_BME == True:
    from bme280 import bme280


class QCustomLabel(QLabel):
    def __init__(self, text):
        super(QCustomLabel, self).__init__(text)

        self.font = QFont('源ノ角ゴシック Code JP N', 11)
        # self.font = QFont('Digital-7', 11)

        self.setFont(self.font)
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.setContentsMargins(-5, -5, -5, -5)
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
    def __init__(self):
        self.date = QCustomLabel('')
        self.times = []
        self.forecastTimes = []
        self.forecastTimesUnit = QCustomLabel('')
        self.forecastWeathers = []
        self.forecastWeathersUnit = QCustomLabel('')
        self.forecastTemps = []
        self.forecastTempssUnit = QCustomLabel('')
        self.forecastRains = []
        self.forecastRainsUnit = QCustomLabel('')
        self.temp = QCustomLabel('')
        self.tempUnit = QCustomLabel('')
        self.hum = QCustomLabel('')
        self.humUnit = QCustomLabel('')
        self.pres = QCustomLabel('')
        self.presUnit = QCustomLabel('')

        if USE_BME == True:
            self.bme = bme280()
            self.bme.initialize()

    def initializeDisplayItems(self):
        initTimes = ['23', ':', '45', '01']
        initForecastTimes = ['21', '0', '3', '6', '9', '12', '15']
        initForecastWeathers = ['☁', '☀', '☀', '☁', '☁/☂', '☂', '☔']
        initForecastTemps = ['16', '12', '10', '12', '16', '20', '20']
        initForecastRains = ['0', '0', '0', '0', '2', '2', '6']

        self.date.setText('2018/5/16 (水)')

        for i in range(0, 4):
            self.times.append(QCustomLabel(''))
            self.times[-1].setText(initTimes[i])
            self.times[-1].setFontScale(1.3)

        self.times[3].setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        for i in range(0, 7):
            self.forecastTimes.append(QCustomLabel(''))
            self.forecastTimes[-1].setText(initForecastTimes[i])
            self.forecastTimes[-1].setFontScale(0.7)

            self.forecastWeathers.append(QCustomLabel(''))
            self.forecastWeathers[-1].setText(initForecastWeathers[i])

            self.forecastTemps.append(QCustomLabel(str(i)))
            self.forecastTemps[-1].setText(initForecastTemps[i])
            self.forecastTemps[-1].setFontScale(0.7)

            self.forecastRains.append(QCustomLabel(''))
            self.forecastRains[-1].setText(initForecastRains[i])
            self.forecastRains[-1].setFontScale(0.7)

        self.forecastTimesUnit.setText('時')
        self.forecastTimesUnit.setFontScale(0.7)
        self.forecastWeathersUnit.setText('天気')
        self.forecastWeathersUnit.setFontScale(0.7)
        self.forecastTempssUnit.setText('℃')
        self.forecastTempssUnit.setFontScale(0.7)
        self.forecastRainsUnit.setText('mm')
        self.forecastRainsUnit.setFontScale(0.7)

        self.temp.setText('22')

        self.tempUnit.setText('℃')

        self.hum.setText('38')

        self.humUnit.setText('%')

        self.pres.setText('1011')

        self.presUnit.setText('hPa')

    def initializeDisplayLayout(self, layout):
        # addWidget(obj, row-pos, col-pos, row-span, col-span)
        layout.addWidget(self.date, 0, 0, 1, 15)

        layout.addWidget(self.times[0], 1, 0, 3, 6)
        layout.addWidget(self.times[1], 1, 6, 3, 2)
        layout.addWidget(self.times[2], 1, 8, 3, 6)
        layout.addWidget(self.times[3], 1, 14, 3, 1)

        for i in range(0, 7):
            layout.addWidget(self.forecastTimes[i], 4, i * 2, 1, 2)
            layout.addWidget(self.forecastWeathers[i], 5, i * 2, 2, 2)
            layout.addWidget(self.forecastTemps[i], 7, i * 2, 1, 2)
            layout.addWidget(self.forecastRains[i], 8, i * 2, 1, 2)

        layout.addWidget(self.forecastTimesUnit, 4, 14)
        layout.addWidget(self.forecastWeathersUnit, 5, 14, 2, 1)
        layout.addWidget(self.forecastTempssUnit, 7, 14)
        layout.addWidget(self.forecastRainsUnit, 8, 14)

        layout.addWidget(self.temp, 1, 15, 2, 2)
        layout.addWidget(self.tempUnit, 1, 17, 2, 1)
        layout.addWidget(self.hum, 3, 15, 2, 2)
        layout.addWidget(self.humUnit, 3, 17, 2, 1)
        layout.addWidget(self.pres, 5, 15, 2, 2)
        layout.addWidget(self.presUnit, 5, 17, 2, 1)

        # fill empty grid
        layout.addWidget(QLabel(), 0, 15, 1, 3)
        layout.addWidget(QLabel(), 7, 15, 2, 3)

    # del setViewMode(self):

    def onTimer(self):
        now = datetime.datetime.today()
        self.date.setText(now.strftime('%Y/%m/%d %a'))
        self.times[0].setText(now.strftime('%H'))
        self.times[2].setText(now.strftime('%M'))
        self.times[3].setText(now.strftime('%S'))

        # if now.hour >= 18 and viewMode == False:
        #     self.viewMode = True
        #     setViewMode(True)
        # elif now.hour >= 6 and view == True:
        #     self.viewMode = False
        #     setViewMode(False)

        if USE_BME == True:
            bmeStatuses = self.bme.getStatus()
            self.temp.setText(bmeStatuses[0])
            self.hum.setText(bmeStatuses[1])
            self.pres.setText(bmeStatuses[2])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setHorizontalSpacing(1)
    layout.setVerticalSpacing(1)

    styleNight = 'QWidget{background-color:#407b8e72;} QLabel{color:#DCF7C9; background-color:#262626;}'
    # styleDay = 'QWidget{background-color:#7b8e72;} QLabel{color:#262626; background-color:#F3F9F1;}'
    app.setStyleSheet(styleNight)

    dispItems = ClockDisplay()
    dispItems.initializeDisplayItems()
    dispItems.initializeDisplayLayout(layout)

    window.setLayout(layout)

    timer = QTimer()
    timer.timeout.connect(dispItems.onTimer)
    timer.start(200)

    window.resize(800, 480)
    window.show()
    sys.exit(app.exec_())
