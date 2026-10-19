from bitstring import BitArray
from i2c_api import I2CMaster, I2CTransactionBuilder, RegisterAddress

from i2c_drivers.i2cdriver import I2CMasterI2CDriver

tr = I2CTransactionBuilder()


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
    data = master.read(bmp581_addr)
    assert data is not None
    assert data == BitArray("0b01010000")

    data = master.read_register(bmp581_addr, register=0x01)
    assert data is not None
    assert data == BitArray("0b01010000")

    results = tr.start().address().write(0x01).restart().address(bmp581_addr).read(1).stop().exec(master, bmp581_addr)
    assert results.is_success
    assert results.data == [[BitArray("0b01010000")]]

    # test write_register(...) against "Over-sampling Rate" register (0x36)
    results = master.write_register(bmp581_addr, RegisterAddress(0x36, 1), data=0, read_back=True)
    assert results.is_success
    assert results.data == [[BitArray("0b00000000")]]

    results = master.write_register(bmp581_addr, RegisterAddress(0x36, 1), data="0b01000000", read_back=True)
    assert results.is_success
    assert results.data == [[BitArray("0b01000000")]]

    data = master.read_register(bmp581_addr, register=0x36)
    assert data is not None
    assert data == BitArray("0b01000000")


def test_i2cdriver():
    i2cmaster_check(I2CMasterI2CDriver())


def test_mcp2221():
    i2cmaster_check(I2CMasterI2CDriver())
