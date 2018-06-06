#! /usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QPushButton, QSizePolicy
from pytz import timezone
from subprocess import Popen, PIPE

import datetime
import os
import psutil
import pwd
import sys
import threading
import weatherinfo

USE_CPUTEMP = True
USE_SPDTST = True
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
        self.setContentsMargins(-3, -1, -3, -1)
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
        self._labelUpload = QCustomLabel(' ')
        self._labelDownload = QCustomLabel(' ')
        self._labelPing = QCustomLabel(' ')

        self._labelForecastTimesUnit = QCustomLabel('時')
        self._labelForecastWeathersUnit = QCustomLabel('天気')
        self._labelForecastTempsUnit = QCustomLabel('℃')
        self._labelForecastRainsUnit = QCustomLabel('mm')
        self._labelTemperatureUnit = QCustomLabel('℃')
        self._labelHumidityUnit = QCustomLabel('%')
        self._labelPressureUnit = QCustomLabel('hPa')
        self._labelUploadUnit = QCustomLabel('Mbps')
        self._labelDownloadUnit = QCustomLabel('Mbps')
        self._labelPingUnit = QCustomLabel('ms')

        self._1SecCount = 1
        self._10SecCount = 1
        self._60SecCount = 1
        self._halfHourCount1 = 0
        self._fullMode = False
        self._bme = object

        self._valDateTime = 0
        self._valTemperature = 0
        self._valHumidity = 0
        self._valPressure = 0
        self._valUpload = 0
        self._valDownload = 0
        self._valPing = 0
        self._valCpuUsage = 0
        self._valCpuTemp = 0

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
        self._labelDate.setFontScale(1.2)

        for i in range(0, 4):
            self._labelTimes[i].setFontScale(1.5)
        self._labelTimes[3].setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        for i in range(0, 7):
            self._labelForecastTimes[i].setFontScale(1.0)
            self._labelForecastWeathers[i].setFontFamily('Meteocons')
            self._labelForecastTemps[i].setFontScale(1.0)
            self._labelForecastRains[i].setFontScale(0.8)

        self._labelForecastTimesUnit.setFontScale(0.5)
        self._labelForecastWeathersUnit.setFontScale(0.5)
        self._labelForecastTempsUnit.setFontScale(0.5)
        self._labelForecastRainsUnit.setFontScale(0.5)

        self._labelTemperature.setFontScale(1.4)
        self._labelHumidity.setFontScale(0.8)
        self._labelPressure.setFontScale(1.4)

        self._labelTemperatureUnit.setFontScale(0.5)
        self._labelHumidityUnit.setFontScale(0.5)
        self._labelPressureUnit.setFontScale(0.5)

    def __initializeDisplayLayout(self, layout):
        # addWidget(obj, row-pos, col-pos, row-span, col-span)
        layout.addWidget(self._labelDate, 0, 0, 1, 8)

        layout.addWidget(self._labelTimes[0], 1, 0, 4, 3)
        layout.addWidget(self._labelTimes[1], 1, 3, 4, 1)
        layout.addWidget(self._labelTimes[2], 1, 4, 4, 3)
        layout.addWidget(self._labelTimes[3], 1, 7, 4, 1)

        for i in range(0, 7):
            layout.addWidget(self._labelForecastTimes[i], 5, i)
            layout.addWidget(self._labelForecastWeathers[i], 6, i, 2, 1)
            layout.addWidget(self._labelForecastTemps[i], 8, i)
            layout.addWidget(self._labelForecastRains[i], 9, i)

        layout.addWidget(self._labelForecastTimesUnit, 5, 7)
        layout.addWidget(self._labelForecastWeathersUnit, 6, 7, 2, 1)
        layout.addWidget(self._labelForecastTempsUnit, 8, 7)
        layout.addWidget(self._labelForecastRainsUnit, 9, 7)

        layout.addWidget(self._labelTemperature, 1, 8, 2, 2)
        layout.addWidget(self._labelTemperatureUnit, 1, 10, 2, 1)
        layout.addWidget(self._labelHumidity, 3, 8, 2, 2)
        layout.addWidget(self._labelHumidityUnit, 3, 10, 2, 1)
        layout.addWidget(self._labelPressure, 5, 8, 2, 2)
        layout.addWidget(self._labelPressureUnit, 5, 10, 2, 1)

        layout.addWidget(self._labelUpload, 7, 8, 1, 2)
        layout.addWidget(self._labelUploadUnit, 7, 10, 1, 1)
        layout.addWidget(self._labelDownload, 8, 8, 1, 2)
        layout.addWidget(self._labelDownloadUnit, 8, 10, 1, 1)
        layout.addWidget(self._labelPing, 9, 8, 1, 2)
        layout.addWidget(self._labelPingUnit, 9, 10, 1, 1)

        # Full screen change button
        screenChangeButton = QPushButton()
        screenChangeButton.clicked.connect(self.__changeScreenMode)
        layout.addWidget(screenChangeButton, 0, 8, 1, 3)

        # Fill empty grid
        # layout.addWidget(QLabel(), 7, 8, 3, 3)

    def __changeScreenMode(self):
        if self._fullMode == True:
            self._fullMode = False
            self._window.showNormal()
        else:
            self._fullMode = True
            self._window.showFullScreen()

    def __updateClock(self, now):
        self._labelDate.setText(now.strftime('%Y/%m/%d %a'))
        self._labelTimes[0].setText(now.strftime('%H'))
        self._labelTimes[2].setText(now.strftime('%M'))
        self._labelTimes[3].setText(now.strftime('%S'))

    def __updateRoomInfo(self):
        if USE_BME == True:
            bmeStatuses = self._bme.getStatus()
            self._valTemperature = bmeStatuses[0]
            self._valHumidity = bmeStatuses[1]
            self._valPressure = bmeStatuses[2]
            self._labelTemperature.setText(self._valTemperature)
            self._labelHumidity.setText(self._valHumidity)
            self._labelPressure.setText(self._valPressure)

    def __updateWeather(self):
        weathers = weatherinfo.getWeatherForecast()
        for i in range(0, 7):
            if len(weathers) <= i:
                break

            hour = weathers[i][0].hour
            self._labelForecastTimes[i].setText("{0:1d}".format(hour))

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

    def __updateSpeedTest(self):
        if USE_SPDTST == True:
            thread = threading.Thread(target=self.__updateSpeedTestThread, name="updateSpeedTestThread")
            thread.start()

    def __updateSpeedTestThread(self):
        for line in self.__executeCommand('speedtest'):
            if line.find('Upload: ') >= 0:
                self._valUpload = float(line.split(' ')[1])
            if line.find('Download: ') >= 0:
                self._valDownload = float(line.split(' ')[1])
            if line.find(' ms') >= 0:
                index1 = line.find(']: ') + 3
                index2 = line.find(' ms')
                self._valPing = float(line[index1: index2])
            
        print('upload:{0:.2f} download:{1:.2f} ping:{2:.2f}'.format(self._valUpload, self._valDownload, self._valPing))
        self._labelUpload.setText('{:.1f}'.format(self._valUpload))
        self._labelDownload.setText('{:.1f}'.format(self._valDownload))
        self._labelPing.setText('{:.1f}'.format(self._valPing))

        self.__writeCsvThread()

    def __updateCpuInfo(self):
        thread = threading.Thread(target=self.__updateCpuInfoThread, name="updateCpuInfoThread")
        thread.start()

    def __updateCpuInfoThread(self):
        self._valCpuUsage = psutil.cpu_percent()
        if USE_CPUTEMP == True:
            for line in self.__executeCommand('vcgencmd measure_temp'):
                self._valCpuTemp = float(line.replace("temp=", "").replace("'C", ""))
        #print('CPU usage:{0:.2f}% temp:{1:.2f}'.format(self._valCpuUsage, self._valCpuTemp))

    # def __writeCsv(self):
    #     thread = threading.Thread(target=self.__writeCsvThread, name="writeCsvThread")
    #     thread.start()

    def __writeCsvThread(self):
        path = '/var/www/html/roominfo.csv'
        if os.name == 'nt':
            path = 'www/roominfo.csv'

        fs = open(path, "at+")
        fs.seek(0)
        read = []
        for line in fs.readlines():
            read.append(line)
        fs.close()

        read.append(self.__getRoomInfoOneLine())

        fs = open(path, "wt+")
        fs.seek(0, 0)
        for i, w in enumerate(read):
            if len(read) > 24 * 2 * 7:
                if i >= 1:
                    fs.write(w)
            else:
                fs.write(w)
        fs.close()

        if os.name != 'nt':
            mark = pwd.getpwnam('mark')
            os.chown(path, mark.pw_uid, mark.pw_gid)
            os.chmod(path, 0o766)

    def __getRoomInfoOneLine(self):
        return '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}\n'.format(
            self._valDateTime.strftime("%Y/%m/%d %H:%M:%S %z"),
            self._valTemperature, self._valHumidity, self._valPressure,
            self._valCpuTemp,
            self._valUpload, self._valDownload, self._valPing)

    def __executeCommand(self, cmd):
        p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        out = out.decode('utf-8')
        return [s for s in out.split('\n') if s]

    def setNightMode(self):
        styleNight = 'QWidget{background-color:#407b8e72;} QLabel, QPushButton{color:#DCF7C9; background-color:#111111;}'
        self._app.setStyleSheet(styleNight)

    # def setDayMode(self):
    #     styleDay = 'QWidget{background-color:#7b8e72;} QLabel, QPushButton{color:#111111; background-color:#F3F9F1;}'
    #     self._app.setStyleSheet(styleDay)

    def onTimer(self):
        # now = datetime.datetime.today()
        now = datetime.datetime.now(timezone('Asia/Tokyo'))
        self._1SecCount -= 1
        if self._1SecCount == 0:
            self._1SecCount = 5     # 200ms timer / 5 count = 1sec
            self._10SecCount -= 1
            self._60SecCount -= 1

            self.__updateClock(now)

            if (now.minute == 25 or now.minute == 55) and self._60SecCount == 0:
                self._halfHourCount1 -= 1

            # if now.hour == 6 and now.minute == 0 and now.second == 0:
            #     self.setDayMode()

            # if now.hour == 18 and now.minute == 0 and now.second == 0:
            #     self.setNightMode()

            if self._10SecCount == 0:
                self._10SecCount = 10
                self.__updateRoomInfo()
                self.__updateCpuInfo()

            if self._60SecCount == 0:
                self._60SecCount = 60
                # update_ntp_status_thread()

            if self._halfHourCount1 <= 0:
                self._halfHourCount1 = 1
                self._valDateTime = now
                print('{0} -----------'.format(now))
                self.__updateWeather()
                self.__updateSpeedTest()
                print('------------------------')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()

    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setHorizontalSpacing(2)
    layout.setVerticalSpacing(2)

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
