from .ft232h import I2CMasterFT232H
from .i2cdriver import I2CMasterI2CDriver
from .mcp2221 import I2CMasterMCP2221

I2CAPI_IMPL = [I2CMasterMCP2221, I2CMasterI2CDriver, I2CMasterFT232H]
