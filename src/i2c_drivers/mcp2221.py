from functools import partial
from typing import override

import EasyMCP2221
from bitstring import BitArray, Bits
from i2c_api import (
    ExecResults,
    I2CLogger,
    I2CMaster,
)
from i2c_api.commands import Data, P, Read, S, Sr, W
from i2c_api.language import I2CTransaction


class I2CMasterMCP2221(I2CMaster):
    def __init__(self, logger: I2CLogger | None = None):
        super().__init__(logger)
        self.driver = EasyMCP2221.Device()
        self.__speed = 100

    def close(self):
        pass

    @override
    def scan(self) -> list[int]:
        found_devices = []
        for addr in range(0x7F):
            try:
                self.driver.I2C_read(addr)
                found_devices.append(addr)
            except EasyMCP2221.exceptions.NotAckError:
                pass
        return found_devices

    @override
    def list_pullups(self) -> list[str]:
        return ["5.1K"]

    @override
    def set_pullup(self, pullup_value: str) -> None:
        if pullup_value != "5.1K":
            raise ValueError("Invalid resistor pullup value")

    @override
    def get_pullup(self) -> str:
        return "5.1K"

    @override
    def list_clk_speeds(self) -> list[int]:
        return [47, 100, 200, 300, 400]

    @override
    def get_clk_speed(self) -> int:
        return self.__speed

    @override
    def set_clk_speed(self, speed: int) -> None:
        if speed in self.list_clk_speeds():
            self.driver.I2C_speed(speed * 1000)
            self.__speed = speed
        else:
            raise ValueError("Unsupported clock speed")

    @override
    def _exec(self, transaction: "I2CTransaction", device_address: int = -1) -> ExecResults:
        calls = []
        cmds = []
        data_rsp = []
        nack = []

        def handle_write(kind: str):
            calls.append(
                partial(
                    self.driver.I2C_write,
                    addr=device_address if cmds[1].address == -1 else cmds[1].address,
                    data=I2CMaster.mk_payload([c.data for c in cmds if isinstance(c, Data)]).bytes,
                    kind=kind,
                )
            )
            cmds.clear()

        def handle_read(kind: str):
            calls.append(
                partial(
                    self.driver.I2C_read,
                    addr=device_address if cmds[1].address == -1 else cmds[1].address,
                    size=cmds[2].num_bytes,
                    kind=kind,
                )
            )
            cmds.clear()

        for cmd in transaction._i2c._i2c_commands:
            cmds.append(cmd)
            match cmds[0], cmds[-1]:
                case S(), P():
                    if isinstance(cmds[2], W):
                        handle_write("regular")
                    elif isinstance(cmds[2], Read):
                        handle_read("regular")
                    else:
                        raise ValueError(f"Unknown command in {transaction}")

                case S(), Sr():
                    if isinstance(cmds[2], W):
                        handle_write("nonstop")
                        cmds.append(Sr())
                    elif isinstance(cmds[2], Read):
                        raise ValueError("Read transaction must end with stop")
                    else:
                        raise ValueError(f"Unknown command in {transaction}")

                case Sr(), Sr():
                    raise ValueError("Transaction after restart must end with stop")

                case Sr(), P():
                    if isinstance(cmds[2], W):
                        handle_write("restart")
                    elif isinstance(cmds[2], Read):
                        handle_read("restart")
                    else:
                        raise ValueError(f"Unknown command in {transaction}")
        for c in calls:
            try:
                response = c()
                if response is not None:
                    data_from_the_client = Bits(response)
                    data_rsp.append([BitArray(f"uint:8={x}") for x in data_from_the_client.tobytes()])
            except Exception as ex:
                nack.append(ex)

        return ExecResults(data=[[BitArray(f"uint:8={c.uint}") for c in d] for d in data_rsp], is_success=(nack == []))
