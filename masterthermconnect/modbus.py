"""This provides an API for the Modbus local access."""

import logging

from pymodbus.client import AsyncModbusTcpClient

_LOGGER: logging.Logger = logging.getLogger(__name__)


class MasterthermModbus:
    """Modbus API for Mastertherm Heatpumps."""

    def __init__(self, addr: str) -> None:
        """Initialise the Modbus API."""
        self._addr = addr

    async def connect(self) -> bool:
        """Connect to the Modbus Client."""
        client = AsyncModbusTcpClient(self._addr)
        try:
            await client.connect()
        except Exception as e:
            _LOGGER.error(f"Error connecting to Modbus: {e}")
            return False

        return True
