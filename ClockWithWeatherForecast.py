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

        self.setFont(self.font)
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.setContentsMargins(-2, -2, -2, -2)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.SizePolicyEz(2, 1)

    # def setFontSize(self, size):
    #     self.font.setPointSize(size)
    #     self.setFont(self.font)

    def SizePolicyEz(self, h, v):
        sizePolicy = self.sizePolicy()
        sizePolicy.setHorizontalStretch(h)
        sizePolicy.setVerticalStretch(v)
        self.setSizePolicy(sizePolicy)

    def resizeEvent(self, evt):
        baseSize = 0
        if self.size().width() > self.size().height():
            baseSize = self.size().height()
        else:
            baseSize = self.size().width()
            
        self.font.setPixelSize(baseSize * 0.7)
        self.setFont(self.font)

class ClockDisplay:
    def __init__(self):
        self.date = QCustomLabel('')
        self.times = []
        self.forecastTimes = []
        self.forecastWeathers = []
        self.forecastTemps = []
        self.forecastRains = []
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
        # initTimesSize = [72, 48, 72, 18]
        initForecastTimes = ['21', '0', '3', '6', '9', '12', '15', '時']
        initForecastWeathers = ['☁', '☀', '☀', '☁', '☁/☂', '☂', '⛆', '天気']
        # initForecastWeathersSize = [26, 26, 26, 26, 11, 26, 26, 12]
        initForecastTemps = ['16', '12', '10', '12', '16', '20', '20', '℃']
        initForecastRains = ['0', '0', '0', '0', '2', '2', '6', '雨量']

        self.date.setText('2018/5/16 (水)')
        # self.date.setFontSize(24)
        self.date.SizePolicyEz(4, 1)

        for i in range(0, 4):
            self.times.append(QCustomLabel(''))
            self.times[-1].setText(initTimes[i])
            # self.times[-1].setFontSize(initTimesSize[i])
            self.times[-1].SizePolicyEz(3, 2)

        self.times[3].setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        for i in range(0, 8):
            self.forecastTimes.append(QCustomLabel(''))
            self.forecastTimes[-1].setText(initForecastTimes[i])

            self.forecastWeathers.append(QCustomLabel(''))
            self.forecastWeathers[-1].setText(initForecastWeathers[i])
            # self.forecastWeathers[-1].setFontSize(initForecastWeathersSize[i])
            # if i != 7:
            self.forecastWeathers[-1].SizePolicyEz(1, 2)

            self.forecastTemps.append(QCustomLabel(str(i)))
            self.forecastTemps[-1].setText(initForecastTemps[i])

            self.forecastRains.append(QCustomLabel(''))
            self.forecastRains[-1].setText(initForecastRains[i])

        self.temp.setText('22')
        # self.temp.setFontSize(28)
        self.temp.SizePolicyEz(2, 2)

        self.tempUnit.setText('℃')
        # self.tempUnit.setFontSize(20)

        self.hum.setText('38')
        # self.hum.setFontSize(28)
        self.hum.SizePolicyEz(2, 2)

        self.humUnit.setText('%')
        # self.humUnit.setFontSize(20)

        self.pres.setText('1011')
        # self.pres.setFontSize(20)
        self.pres.SizePolicyEz(2, 1)

        self.presUnit.setText('hPa')
        # self.presUnit.setFontSize(11)

    def initializeDisplayLayout(self, layout):
        # addWidget(obj, row-pos, col-pos, row-span, col-span)
        layout.addWidget(self.date, 0, 0, 1, 8)

        layout.addWidget(self.times[0], 1, 0, 2, 3)
        layout.addWidget(self.times[1], 1, 3, 2, 1)
        layout.addWidget(self.times[2], 1, 4, 2, 3)
        layout.addWidget(self.times[3], 1, 7, 2, 1)

        for i in range(0, 8):
            layout.addWidget(self.forecastTimes[i], 3, i)
            layout.addWidget(self.forecastWeathers[i], 4, i)
            layout.addWidget(self.forecastTemps[i], 5, i)
            layout.addWidget(self.forecastRains[i], 6, i)

        layout.addWidget(self.temp, 1, 8)
        layout.addWidget(self.tempUnit, 1, 9)
        layout.addWidget(self.hum, 2, 8)
        layout.addWidget(self.humUnit, 2, 9)
        layout.addWidget(self.pres, 3, 8, 2, 1)
        layout.addWidget(self.presUnit, 3, 9, 2, 1)

        # fill empty grid
        layout.addWidget(QLabel(), 0, 8, 1, 2)
        layout.addWidget(QLabel(), 5, 8, 2, 2)

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

    styleNight = 'QWidget{background-color:#7b8e72;} QLabel{color:#DCF7C9; background-color:#262626;}'
    # styleDay = 'QWidget{background-color:#7b8e72;} QLabel{color:#262626; background-color:#F3F9F1;}'
    app.setStyleSheet(styleNight)

    dispItems = ClockDisplay()
    dispItems.initializeDisplayItems()
    dispItems.initializeDisplayLayout(layout)

    window.setLayout(layout)

    timer = QTimer()
    timer.timeout.connect(dispItems.onTimer)
    timer.start(200)

    window.show()
    sys.exit(app.exec_())
