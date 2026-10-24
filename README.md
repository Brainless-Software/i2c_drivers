# I²C Drivers

[![License - MIT](https://img.shields.io/badge/License-MIT-blue)](https://github.com/Brainless-Software/i2c_drivers/blob/master/LICENSE)
[![PyPI Latest Release](https://img.shields.io/pypi/v/i2c-drivers.svg)](https://pypi.org/project/i2c-drivers/)

Implementations of [i2c_api](https://brainless-software.github.io/i2c_api/) (Python) for various dongles.
Dongles are usually USB-to-I2C bridges that act as I2C master devices and allows one to talk I2C slave devices present
on the I2C bus.

Following dongles are supported:

* [I2CDriver](https://i2cdriver.com/)
* [MCP2221](https://www.adafruit.com/product/4471) (official chip link is [here](https://www.microchip.com/en-us/product/mcp2221))
* [FT232H](https://www.adafruit.com/product/2264)

To add this library to your project do

```shell
uv add i2c_drivers
```

On how to use these drivers see documentation for [i2c_api](https://brainless-software.github.io/i2c_api/).
