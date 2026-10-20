from bitstring import BitArray
from i2c_api import I2CLogger, I2CMaster, I2CTransactionBuilder, RegisterAddress
from i2c_api.log import I2CTransactionElement

from i2c_drivers.i2cdriver import I2CMasterI2CDriver
from i2c_drivers.mcp2221 import I2CMasterMCP2221

tr = I2CTransactionBuilder()


class ALogger(I2CLogger):
    def __init__(self):
        self.messages: list[list[I2CTransactionElement]] = []

    def log_message(self, message: list[I2CTransactionElement]):
        self.messages.append(message)


def i2cmaster_check(master: I2CMaster):
    """
    Test I2CMaster against BMP581
    """
    bmp581_addr = 0x47

    devices = master.scan()
    assert len(devices) == 1
    assert devices[0] == bmp581_addr  # default address for BMP581

    # read CHIP_ID (0x01) using three methods
    master.write(bmp581_addr, 0x01)  # selects register address 0x01
    assert (
        str(master.logger().messages[-1])
        == "[START(), DATA_MOSI(0b1000111), WRITE(), ACK(), DATA_MOSI(0x01), ACK(), STOP()]"
    )
    data = master.read(bmp581_addr)
    assert (
        str(master.logger().messages[-1])
        == "[START(), DATA_MOSI(0b1000111), READ(), ACK(), DATA_MISO(0x50), ACK(), STOP()]"
    )
    assert data is not None
    assert data == BitArray("0b01010000")

    data = master.read_register(bmp581_addr, register=0x01, use_restart=True)
    assert data is not None
    assert data == BitArray("0b01010000")

    data = master.read_register(bmp581_addr, register=0x01, use_restart=False)
    assert data is not None
    assert data == BitArray("0b01010000")

    transaction = tr.start().address().write(0x01).restart().address(bmp581_addr).read(1).stop()
    results = transaction.exec(master, bmp581_addr)
    assert results.is_success
    assert results.data == [[BitArray("0b01010000")]]

    # test write_register(...) against "Over-sampling Rate" register (0x36)
    data = master.write_register(bmp581_addr, RegisterAddress(0x36, 1), data=0, read_back=True)
    assert data is not None
    assert data == BitArray("0b00000000")

    data = master.write_register(bmp581_addr, RegisterAddress(0x36, 1), data="0b01000000", read_back=True)
    assert data is not None
    assert data == BitArray("0b01000000")

    data = master.read_register(bmp581_addr, register=0x36)
    assert data is not None
    assert data == BitArray("0b01000000")


def test_i2cdriver():
    with I2CMasterI2CDriver(logger=ALogger()) as master:
        i2cmaster_check(master)


def test_mcp2221():
    with I2CMasterMCP2221(ALogger()) as master:
        i2cmaster_check(master)
