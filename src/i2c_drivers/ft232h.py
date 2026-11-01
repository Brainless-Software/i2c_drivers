from bitstring import BitArray
from i2c_api import ExecResults, I2CLogger, I2CMaster, I2CMasterProvider, I2CTransaction
from i2c_api.commands import Address, Data, P, Read, S, Sr, W
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController
from pyftdi.usbtools import UsbTools


class I2CMasterFT232H(I2CMaster):
    def __init__(self, url="ftdi://ftdi:232h:1/1", logger: I2CLogger | None = None) -> None:
        super().__init__(url, logger)
        self.driver = I2cController()
        self.driver.configure(url, frequency=100000)
        self.__speed = 100

    def display_name(self) -> str:
        return f"FTDI :: FT232H :: {self.port}"

    def _exec(self, transaction: I2CTransaction, device_address: int = -1) -> ExecResults:
        device_address = -1
        action = ""
        data_out = []
        num_bytes_to_read = -1
        failure = []
        response_data: list[list[BitArray]] = []

        def write_call(device_address: int, data_out: list[int], stop: bool) -> None:
            try:
                self.driver.write(device_address, data_out, relax=stop)
            except Exception as ex:
                failure.append(ex)

        def read_call(device_address: int, num_bytes_to_read: int, stop: bool) -> None:
            try:
                response = self.driver.read(device_address, num_bytes_to_read, relax=stop)
                response_data.append([BitArray(f"uint:8={b}") for b in response])
            except Exception as ex:
                failure.append(ex)

        for cmd in transaction._i2c._i2c_commands:
            match cmd:
                case S():
                    pass
                case Address(address):
                    device_address = address
                case W():
                    action = "write"
                case Data(data):
                    data_out.append(data)
                case Sr():
                    if action == "write":
                        write_call(device_address, data_out, stop=False)
                    else:  # read
                        read_call(device_address, num_bytes_to_read, stop=False)
                    if any(failure):
                        return ExecResults(response_data, is_success=False)
                case Read(num_bytes):
                    num_bytes_to_read = num_bytes
                    action = "read"
                case P():
                    if action == "write":
                        write_call(device_address, data_out, stop=True)
                    else:  # read
                        read_call(device_address, num_bytes_to_read, stop=True)
                    return ExecResults(response_data, is_success=not any(failure))

        return ExecResults([], is_success=False)

    def scan(self) -> list[int]:
        devices: list[int] = []
        for address in range(0x08, I2cController.HIGHEST_I2C_ADDRESS + 1):
            try:
                p = self.driver.poll(address)
                if p:
                    devices.append(address)
            except Exception:
                pass
        return devices

    def list_pullups(self) -> list[str]:
        return ["75K"]

    def set_pullup(self, pullup_value: str) -> None:
        if pullup_value != "75K":
            raise ValueError("Invalid resistor pullup value")

    def get_pullup(self) -> str:
        return "75K"

    def list_clk_speeds(self) -> list[int]:
        return [100, 400, 1000, 3400]

    def get_clk_speed(self) -> int:
        return self.__speed

    def set_clk_speed(self, speed: int) -> None:
        if speed in self.list_clk_speeds():
            self.driver._ftdi._set_frequency(speed * 1000)
            self.__speed = speed
        else:
            raise ValueError("Unsupported clock speed")

    def close(self):
        self.driver.close()


def get_ports() -> list[str]:
    return [
        d[0]
        for d in UsbTools.build_dev_strings("ftdi", Ftdi.VENDOR_IDS, Ftdi.PRODUCT_IDS, Ftdi.list_devices())
        if "232h" in d[0]
    ]


I2CMasterProviderFT232H = I2CMasterProvider(
    make="FTDI",
    model="FT232H",
    new_i2c_master=lambda port, logger: I2CMasterFT232H(port, logger),
    ports_required=True,
    list_ports=get_ports,
)
