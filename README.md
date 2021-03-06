# ClockWithWeatherForecast

![img](/spec/example_displayed_in_raspberry_pie.jpg)

## Description

It is an application of clock with weather forecast for PyQt5

* Display of date and time
* Display of temperature and humidiry (require BME280 sensor)
* Display of 1 day / 3 hour forecast (require api key of openweathermap.org)

## Require

### Hardware

* Raspberry pi 1 Model B+ or later.

### Software

* Python3 or later

You need to install the following:

```sh
pip install pyqt5
pip install pytz
pip install dotenv
pip install requests

sudo apt install -y python3-smbus
```

Default use fonts is below. But you can use your favorite fonts.

* [source han code JP](https://github.com/adobe-fonts/source-han-code-jp)
* [Meteocons](http://www.alessioatzeni.com/meteocons/)

Thanks to everything!
