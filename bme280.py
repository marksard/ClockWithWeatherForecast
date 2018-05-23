#! /usr/bin/python3
# -*- coding: utf-8 -*-

import smbus

# ***************************
# I2C (BME280) Settings
# This code is used by editing the following sample code.
# https://github.com/SWITCHSCIENCE/samplecodes/tree/master/BME280

I2cBusNumber = 1    # Maybe differeced by environment(0 or 1)
I2cAddress = 0x76   # Maybe differeced by each devices
I2cBusInstance = smbus.SMBus(I2cBusNumber)
I2cCaribTemp = []
I2cCaribPress = []
I2cCaribHumi = []
I2cCaribFine = 0.0

class bme280:
    def __init__(self):
        self.__initialize()
        self.__calibration()

    def __initialize(self):
        osrs_t = 1  # Temperature oversampling x 1
        osrs_p = 1  # Pressure oversampling x 1
        osrs_h = 1  # Humidity oversampling x 1
        mode = 3  # Normal mode
        t_sb = 5  # Tstandby 1000ms
        filter = 0  # Filter off
        spi3w_en = 0  # 3-wire SPI Disable

        ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
        config_reg = (t_sb << 5) | (filter << 2) | spi3w_en
        ctrl_hum_reg = osrs_h

        self.__writeDataI2C(0xF2, ctrl_hum_reg)
        self.__writeDataI2C(0xF4, ctrl_meas_reg)
        self.__writeDataI2C(0xF5, config_reg)


    def __calibration(self):
        calib = []

        for i in range(0x88, 0x88 + 24):
            calib.append(I2cBusInstance.read_byte_data(I2cAddress, i))

        calib.append(I2cBusInstance.read_byte_data(I2cAddress, 0xA1))

        for i in range(0xE1, 0xE1 + 7):
            calib.append(I2cBusInstance.read_byte_data(I2cAddress, i))

        I2cCaribTemp.append((calib[1] << 8) | calib[0])
        I2cCaribTemp.append((calib[3] << 8) | calib[2])
        I2cCaribTemp.append((calib[5] << 8) | calib[4])
        I2cCaribPress.append((calib[7] << 8) | calib[6])
        I2cCaribPress.append((calib[9] << 8) | calib[8])
        I2cCaribPress.append((calib[11] << 8) | calib[10])
        I2cCaribPress.append((calib[13] << 8) | calib[12])
        I2cCaribPress.append((calib[15] << 8) | calib[14])
        I2cCaribPress.append((calib[17] << 8) | calib[16])
        I2cCaribPress.append((calib[19] << 8) | calib[18])
        I2cCaribPress.append((calib[21] << 8) | calib[20])
        I2cCaribPress.append((calib[23] << 8) | calib[22])
        I2cCaribHumi.append(calib[24])
        I2cCaribHumi.append((calib[26] << 8) | calib[25])
        I2cCaribHumi.append(calib[27])
        I2cCaribHumi.append((calib[28] << 4) | (0x0F & calib[29]))
        I2cCaribHumi.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
        I2cCaribHumi.append(calib[31])

        for i in range(1, 2):
            if I2cCaribTemp[i] & 0x8000:
                I2cCaribTemp[i] = (-I2cCaribTemp[i] ^ 0xFFFF) + 1

        for i in range(1, 8):
            if I2cCaribPress[i] & 0x8000:
                I2cCaribPress[i] = (-I2cCaribPress[i] ^ 0xFFFF) + 1

        for i in range(0, 6):
            if I2cCaribHumi[i] & 0x8000:
                I2cCaribHumi[i] = (-I2cCaribHumi[i] ^ 0xFFFF) + 1


    def getStatus(self):
        data = []
        for i in range(0xF7, 0xF7 + 8):
            data.append(I2cBusInstance.read_byte_data(I2cAddress, i))

        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        return [self.__getTemperature(temp_raw), self.__getHumidity(hum_raw), self.__getPressure(pres_raw)]


    def __writeDataI2C(self, reg_address, data):
        I2cBusInstance.write_byte_data(I2cAddress, reg_address, data)


    def __getPressure(self, data):
        global I2cCaribFine

        v1 = (I2cCaribFine / 2.0) - 64000.0
        v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * I2cCaribPress[5]
        v2 = v2 + ((v1 * I2cCaribPress[4]) * 2.0)
        v2 = (v2 / 4.0) + (I2cCaribPress[3] * 65536.0)
        v1 = (((I2cCaribPress[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)
                ) / 8) + ((I2cCaribPress[1] * v1) / 2.0)) / 262144
        v1 = ((32768 + v1) * I2cCaribPress[0]) / 32768

        if v1 == 0:
            return 0

        pressure = ((1048576 - data) - (v2 / 4096)) * 3125

        if pressure < 0x80000000:
            pressure = (pressure * 2.0) / v1
        else:
            pressure = (pressure / v1) * 2

        v1 = (I2cCaribPress[8] * (((pressure / 8.0)
                                * (pressure / 8.0)) / 8192.0)) / 4096
        v2 = ((pressure / 4.0) * I2cCaribPress[7]) / 8192.0
        pressure = pressure + ((v1 + v2 + I2cCaribPress[6]) / 16.0)

        return str("%3.0f" % (pressure / 100))


    def __getTemperature(self, data):
        global I2cCaribFine
        v1 = (data / 16384.0 - I2cCaribTemp[0] / 1024.0) * I2cCaribTemp[1]
        v2 = (data / 131072.0 - I2cCaribTemp[0] / 8192.0) * (
            data / 131072.0 - I2cCaribTemp[0] / 8192.0) * I2cCaribTemp[2]
        I2cCaribFine = v1 + v2
        temperature = I2cCaribFine / 5120.0
        return str("%4.1f" % temperature)


    def __getHumidity(self, data):
        global I2cCaribFine
        var_h = I2cCaribFine - 76800.0
        if var_h != 0:
            var_h = (data - (I2cCaribHumi[3] * 64.0 + I2cCaribHumi[4] / 16384.0 * var_h)) * (
                I2cCaribHumi[1] / 65536.0 * (1.0 + I2cCaribHumi[5] / 67108864.0 * var_h * (1.0 + I2cCaribHumi[2] / 67108864.0 * var_h)))
        else:
            return 0

        var_h = var_h * (1.0 - I2cCaribHumi[0] * var_h / 524288.0)

        if var_h > 100.0:
            var_h = 100.0
        elif var_h < 0.0:
            var_h = 0.0

        return str("%2.0f" % var_h)
