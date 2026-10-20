from bitstring import BitArray, Bits
from i2c_api import ExecResults, I2CLogger, I2CMaster, I2CTransaction
from i2c_api.log import I2CTransactionElement
from pyftdi.i2c import I2cController, I2cIOError


class I2CMasterFT232H(I2CMaster):
    def __init__(self, url="ftdi://ftdi:232h:1/1", logger: I2CLogger | None = None) -> None:
        super().__init__(logger)
        self.driver = I2cController()
        self.driver.configure(url, frequency=100000)
        self.__speed = 100

    def _write(
        self,
        address: int,
        *,
        data: Bits | str | int | list[int],
        log_msg: list[I2CTransactionElement],
        num_bytes: int | None,
        end_with_stop: bool,
        start_with_restart: bool,
    ) -> bool:
        try:
            self.driver.write(address, I2CMaster.mk_payload(data, num_bytes).bytes, relax=(not end_with_stop))
            return True
        except I2cIOError:
            return False

    def _read(
        self,
        address: int,
        *,
        num_bytes: int,
        log_msg: list[I2CTransactionElement],
        end_with_stop: bool,
        start_with_restart: bool,
    ) -> Bits | None:
        try:
            return BitArray(self.driver.read(address, readlen=num_bytes, relax=(not end_with_stop)))
        except I2cIOError:
            return None

    def _exec(self, transaction: I2CTransaction, device_address: int = -1) -> ExecResults:
        pass

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self):
        self.driver.close()
