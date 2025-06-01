"""This provides an API for the Modbus local access."""

import ctypes
import logging
from typing import Any

from pymodbus.client import AsyncModbusTcpClient

from masterthermconnect.modbusmap import MAPPING

_LOGGER: logging.Logger = logging.getLogger(__name__)


class MasterthermModbus:
    """Modbus API for Mastertherm Heatpumps."""

    def __init__(self, addr: str, mt_type: str) -> None:
        """Initialise the Modbus API."""
        if mt_type not in ["mt_0", "mt_1"]:
            _LOGGER.error("Invalid type %s, must be one of mt_0 or mt_1", type)
            raise ValueError("Invalid type, must be one of mt_0 or mt_1")

        self._reg_map = MAPPING[mt_type]
        self._client = AsyncModbusTcpClient(addr)

    async def connect(self) -> bool:
        """Connect to the Modbus Client."""
        try:
            await self._client.connect()
        except Exception as e:
            _LOGGER.error(f"Error connecting to Modbus: {e}")
            return False

        return True

    def close(self) -> None:
        """Close the Modbus Client connection."""
        self._client.close()

    async def _read_a_registers(self, slave: int) -> dict[str, Any]:
        """Read all A registers from the slave."""
        reg: dict[str, Any] = {}

        start = self._reg_map["A"]["start"]
        for i in range(0, 6):
            result = await self._client.read_holding_registers(
                (i * 100), count=100, slave=slave
            )
            for j in range(0, 100):
                reg[f"A_{(i * 100) + j}"] = (
                    float(ctypes.c_short(result.registers[j]).value) / 10.0
                )

        return reg

    async def _read_i_registers(self, slave: int) -> dict[str, Any]:
        """Read all I registers from the slave."""
        reg: dict[str, Any] = {}

        start = self._reg_map["I"]["start"]
        for i in range(0, 6):
            result = await self._client.read_holding_registers(
                (i * 100) + start, count=100, slave=slave
            )
            for j in range(0, 100):
                reg[f"I_{(i * 100) + j}"] = ctypes.c_short(result.registers[j]).value

        return reg

    async def _read_d_registers(self, slave: int) -> dict[str, Any]:
        """Read all D registers from the slave."""
        reg: dict[str, Any] = {}
        start = self._reg_map["D"]["start"]
        reg_type = self._reg_map["D"]["type"]
        for i in range(0, 6):
            match reg_type:
                case "hold":
                    result = await self._client.read_holding_registers(
                        (i * 100) + start, count=100, slave=slave
                    )
                case "coil":
                    result = await self._client.read_coils(
                        (i * 100) + start, count=100, slave=slave
                    )

            for j in range(0, 100):
                reg[f"D_{(i * 100) + j}"] = result.bits[j]

        return reg

    async def _read_registers(
        self, slave: int, reg_type: str, start: int
    ) -> dict[str, Any]:
        """Read all registers from the slave."""
        reg: dict[str, Any] = {}

        for i in range(0, 6):
            match reg_type:
                case "hold":
                    result = await self._client.read_holding_registers(
                        (i * 100) + start, count=100, slave=slave
                    )
                case "coil":
                    result = await self._client.read_coils(
                        (i * 100) + start, count=100, slave=slave
                    )

            for j in range(0, 100):
                reg[f"I_{(i * 100) + j}"] = ctypes.c_short(result.registers[j]).value

        return reg

    async def get_registers(self, slave: int) -> dict[str, Any]:
        """Read All A, D and I Registers and return."""
        reg: dict[str, Any] = {}

        reg.update(await self._read_a_registers(slave))
        reg.update(await self._read_d_registers(slave))
        reg.update(await self._read_i_registers(slave))

        return reg
