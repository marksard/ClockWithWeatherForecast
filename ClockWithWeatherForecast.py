#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel

class QCustomLabel(QLabel):
    def __init__(self, text):
        super(QCustomLabel, self).__init__(text)

        self.font = QFont("源ノ角ゴシック Code JP N", 11)

        self.setFont(self.font)
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)

    def setFontSize(self, size):
        self.font.setPointSize(size)
        self.setFont(self.font)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QGridLayout()

    style = 'QWidget{color:#DCF7C9; background-color:#262626}'
    app.setStyleSheet(style)

    # addWidget(obj, row-pos, col-pos, row-span, col-span)

    date = QCustomLabel("2018/5/16 (水)")
    date.setFontSize(24)
    layout.addWidget(date, 0, 0, 1, 8)

    times = []
    times.append(QCustomLabel("23"))
    times.append(QCustomLabel(":"))
    times.append(QCustomLabel("45"))
    times.append(QCustomLabel("01"))


    times[0].setFontSize(72)
    times[1].setFontSize(72)
    times[2].setFontSize(72)
    times[3].setFontSize(18)
    times[3].setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
    layout.addWidget(times[0], 1, 0, 2, 3)
    layout.addWidget(times[1], 1, 3, 2, 1)
    layout.addWidget(times[2], 1, 4, 2, 3)
    layout.addWidget(times[3], 1, 7, 2, 1)

    forecastTimes = []
    # for i in range(0, 8):
    #     forecastTimes.append(QCustomLabel(str((i*3) % 24)))
    # forecastTimes[7].setText("時")
    forecastTimes.append(QCustomLabel("21"))
    forecastTimes.append(QCustomLabel("0"))
    forecastTimes.append(QCustomLabel("3"))
    forecastTimes.append(QCustomLabel("6"))
    forecastTimes.append(QCustomLabel("9"))
    forecastTimes.append(QCustomLabel("12"))
    forecastTimes.append(QCustomLabel("15"))
    forecastTimes.append(QCustomLabel("時"))

    layout.addWidget(forecastTimes[0], 3, 0)
    layout.addWidget(forecastTimes[1], 3, 1)
    layout.addWidget(forecastTimes[2], 3, 2)
    layout.addWidget(forecastTimes[3], 3, 3)
    layout.addWidget(forecastTimes[4], 3, 4)
    layout.addWidget(forecastTimes[5], 3, 5)
    layout.addWidget(forecastTimes[6], 3, 6)
    layout.addWidget(forecastTimes[7], 3, 7)

    forecastWeathers = []
    # for i in range(0, 8):
    #     forecastWeathers.append(QCustomLabel("wz"+str(i)))
    forecastWeathers.append(QCustomLabel("⛅"))
    forecastWeathers.append(QCustomLabel("☀"))
    forecastWeathers.append(QCustomLabel("☀"))
    forecastWeathers.append(QCustomLabel("☁"))
    forecastWeathers.append(QCustomLabel("☁/🌂"))
    forecastWeathers.append(QCustomLabel("🌂"))
    forecastWeathers.append(QCustomLabel("☔"))
    forecastWeathers.append(QCustomLabel("天気"))
    for i in range(0, 7):
        forecastWeathers[i].setFontSize(26)
    forecastWeathers[4].setFontSize(12)

    layout.addWidget(forecastWeathers[0], 4, 0)
    layout.addWidget(forecastWeathers[1], 4, 1)
    layout.addWidget(forecastWeathers[2], 4, 2)
    layout.addWidget(forecastWeathers[3], 4, 3)
    layout.addWidget(forecastWeathers[4], 4, 4)
    layout.addWidget(forecastWeathers[5], 4, 5)
    layout.addWidget(forecastWeathers[6], 4, 6)
    layout.addWidget(forecastWeathers[7], 4, 7)

    forecastTemps = []
    # for i in range(0, 8):
    #     forecastTemps.append(QCustomLabel(str(i)))
    # forecastTemps[7].setText("℃")
    forecastTemps.append(QCustomLabel("16"))
    forecastTemps.append(QCustomLabel("12"))
    forecastTemps.append(QCustomLabel("10"))
    forecastTemps.append(QCustomLabel("12"))
    forecastTemps.append(QCustomLabel("16"))
    forecastTemps.append(QCustomLabel("20"))
    forecastTemps.append(QCustomLabel("20"))
    forecastTemps.append(QCustomLabel("℃"))

    layout.addWidget(forecastTemps[0], 5, 0)
    layout.addWidget(forecastTemps[1], 5, 1)
    layout.addWidget(forecastTemps[2], 5, 2)
    layout.addWidget(forecastTemps[3], 5, 3)
    layout.addWidget(forecastTemps[4], 5, 4)
    layout.addWidget(forecastTemps[5], 5, 5)
    layout.addWidget(forecastTemps[6], 5, 6)
    layout.addWidget(forecastTemps[7], 5, 7)

    forecastRains = []
    # for i in range(0, 8):
    #     forecastRains.append(QCustomLabel("rain"+str(i)))
    # forecastRains[7].setText("雨量")
    forecastRains.append(QCustomLabel("0"))
    forecastRains.append(QCustomLabel("0"))
    forecastRains.append(QCustomLabel("0"))
    forecastRains.append(QCustomLabel("0"))
    forecastRains.append(QCustomLabel("2"))
    forecastRains.append(QCustomLabel("2"))
    forecastRains.append(QCustomLabel("6"))
    forecastRains.append(QCustomLabel("雨量"))

    layout.addWidget(forecastRains[0], 6, 0)
    layout.addWidget(forecastRains[1], 6, 1)
    layout.addWidget(forecastRains[2], 6, 2)
    layout.addWidget(forecastRains[3], 6, 3)
    layout.addWidget(forecastRains[4], 6, 4)
    layout.addWidget(forecastRains[5], 6, 5)
    layout.addWidget(forecastRains[6], 6, 6)
    layout.addWidget(forecastRains[7], 6, 7)

    temp = QCustomLabel("22")
    temp.setFontSize(28)
    layout.addWidget(temp, 1, 8)
    tempUnit = QCustomLabel("℃")
    tempUnit.setFontSize(20)
    layout.addWidget(tempUnit, 1, 9)

    hum = QCustomLabel("38")
    hum.setFontSize(28)
    layout.addWidget(hum, 2, 8)
    humUnit = QCustomLabel("%")
    humUnit.setFontSize(20)
    layout.addWidget(humUnit, 2, 9)

    pres = QCustomLabel("1011")
    pres.setFontSize(20)
    layout.addWidget(pres, 3, 8, 2, 1)
    presUnit = QCustomLabel("hPa")
    presUnit.setFontSize(11)
    layout.addWidget(presUnit, 3, 9, 2, 1)

    window.setLayout(layout)

    window.show()
    sys.exit(app.exec_())
