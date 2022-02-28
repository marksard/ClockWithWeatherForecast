# Name: BME280 driver
# Author: marksard
# Version: 1.0
# Python 3.6 or later (maybe)
#   This code is used by editing the following sample code.
#   https://github.com/SWITCHSCIENCE/samplecodes/tree/master/BME280

# ***************************
import smbus

# ***************************
class BME280:
    def __init__(self) -> None:
        self.i2c_bus_number = 1    # Maybe differeced by environment(0 or 1)
        self.__i2c_address = 0x76   # Maybe differeced by each devices
        self.__i2c_bus_instance = smbus.SMBus(self.i2c_bus_number)
        self.__i2c_carib_temp = []
        self.__i2c_carib_press = []
        self.__i2c_carib_humi = []
        self.__i2c_carib_fine = 0.0


    def initialize(self) -> None:
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

        self.__write_data(0xF2, ctrl_hum_reg)
        self.__write_data(0xF4, ctrl_meas_reg)
        self.__write_data(0xF5, config_reg)

        self.__calibration()


    def get_status(self) -> tuple[str, str, str] :
        data = []
        for i in range(0xF7, 0xF7 + 8):
            data.append(self.__i2c_bus_instance.read_byte_data(self.__i2c_address, i))

        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        return self.__get_temperature(temp_raw), self.__get_humidity(hum_raw), self.__get_atmospheric_pressure(pres_raw)


    def __calibration(self) -> None:
        calib = []

        for i in range(0x88, 0x88 + 24):
            calib.append(self.__i2c_bus_instance.read_byte_data(self.__i2c_address, i))

        calib.append(self.__i2c_bus_instance.read_byte_data(self.__i2c_address, 0xA1))

        for i in range(0xE1, 0xE1 + 7):
            calib.append(self.__i2c_bus_instance.read_byte_data(self.__i2c_address, i))

        self.__i2c_carib_temp.append((calib[1] << 8) | calib[0])
        self.__i2c_carib_temp.append((calib[3] << 8) | calib[2])
        self.__i2c_carib_temp.append((calib[5] << 8) | calib[4])
        self.__i2c_carib_press.append((calib[7] << 8) | calib[6])
        self.__i2c_carib_press.append((calib[9] << 8) | calib[8])
        self.__i2c_carib_press.append((calib[11] << 8) | calib[10])
        self.__i2c_carib_press.append((calib[13] << 8) | calib[12])
        self.__i2c_carib_press.append((calib[15] << 8) | calib[14])
        self.__i2c_carib_press.append((calib[17] << 8) | calib[16])
        self.__i2c_carib_press.append((calib[19] << 8) | calib[18])
        self.__i2c_carib_press.append((calib[21] << 8) | calib[20])
        self.__i2c_carib_press.append((calib[23] << 8) | calib[22])
        self.__i2c_carib_humi.append(calib[24])
        self.__i2c_carib_humi.append((calib[26] << 8) | calib[25])
        self.__i2c_carib_humi.append(calib[27])
        self.__i2c_carib_humi.append((calib[28] << 4) | (0x0F & calib[29]))
        self.__i2c_carib_humi.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
        self.__i2c_carib_humi.append(calib[31])

        for i in range(1, 2):
            if self.__i2c_carib_temp[i] & 0x8000:
                self.__i2c_carib_temp[i] = (-self.__i2c_carib_temp[i] ^ 0xFFFF) + 1

        for i in range(1, 8):
            if self.__i2c_carib_press[i] & 0x8000:
                self.__i2c_carib_press[i] = (-self.__i2c_carib_press[i] ^ 0xFFFF) + 1

        for i in range(0, 6):
            if self.__i2c_carib_humi[i] & 0x8000:
                self.__i2c_carib_humi[i] = (-self.__i2c_carib_humi[i] ^ 0xFFFF) + 1


    def __write_data(self, reg_address: int, data: int) -> None:
        self.__i2c_bus_instance.write_byte_data(self.__i2c_address, reg_address, data)


    def __get_atmospheric_pressure(self, data: int) -> str:
        v1 = (self.__i2c_carib_fine / 2.0) - 64000.0
        v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * self.__i2c_carib_press[5]
        v2 = v2 + ((v1 * self.__i2c_carib_press[4]) * 2.0)
        v2 = (v2 / 4.0) + (self.__i2c_carib_press[3] * 65536.0)
        v1 = (((self.__i2c_carib_press[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)
                ) / 8) + ((self.__i2c_carib_press[1] * v1) / 2.0)) / 262144
        v1 = ((32768 + v1) * self.__i2c_carib_press[0]) / 32768

        if v1 == 0:
            return ''

        pressure = ((1048576 - data) - (v2 / 4096)) * 3125

        if pressure < 0x80000000:
            pressure = (pressure * 2.0) / v1
        else:
            pressure = (pressure / v1) * 2

        v1 = (self.__i2c_carib_press[8] * (((pressure / 8.0)
                                * (pressure / 8.0)) / 8192.0)) / 4096
        v2 = ((pressure / 4.0) * self.__i2c_carib_press[7]) / 8192.0
        pressure = pressure + ((v1 + v2 + self.__i2c_carib_press[6]) / 16.0)

        return f'{pressure / 100:3.0f}'


    def __get_temperature(self, data: int) -> str:
        v1 = (data / 16384.0 - self.__i2c_carib_temp[0] / 1024.0) * self.__i2c_carib_temp[1]
        v2 = (data / 131072.0 - self.__i2c_carib_temp[0] / 8192.0) * (
            data / 131072.0 - self.__i2c_carib_temp[0] / 8192.0) * self.__i2c_carib_temp[2]
        self.__i2c_carib_fine = v1 + v2
        temperature = self.__i2c_carib_fine / 5120.0
        return f"{temperature:4.1f}"


    def __get_humidity(self, data: int) -> str:
        var_h = self.__i2c_carib_fine - 76800.0
        if var_h != 0:
            var_h = (data - (self.__i2c_carib_humi[3] * 64.0 + self.__i2c_carib_humi[4] / 16384.0 * var_h)) * (
                self.__i2c_carib_humi[1] / 65536.0 * (1.0 + self.__i2c_carib_humi[5] / 67108864.0 * var_h * (1.0 + self.__i2c_carib_humi[2] / 67108864.0 * var_h)))
        else:
            return ''

        var_h = var_h * (1.0 - self.__i2c_carib_humi[0] * var_h / 524288.0)

        if var_h > 100.0:
            var_h = 100.0
        elif var_h < 0.0:
            var_h = 0.0

        return f'{var_h:2.0f}'
