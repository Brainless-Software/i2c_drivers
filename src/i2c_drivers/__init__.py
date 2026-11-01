from i2c_api import I2CMasterProvider

from .ft232h import I2CMasterFT232H
from .i2cdriver import I2CMasterI2CDriver
from .mcp2221 import I2CMasterMCP2221

I2CAPI_IMPL: list[I2CMasterProvider] = [
    i2cdriver.I2CMasterProviderI2CDriver,
    mcp2221.I2CMasterProviderMCP2221,
    ft232h.I2CMasterProviderFT232H,
]
