"""Mastertherm Controller, for handling Mastertherm Data."""

from aiohttp import ClientSession

from masterthermconnect.api import MasterthermAPI
from masterthermconnect.modbus import MasterthermModbus


class MasterthermController:
    """Mastertherm Integration Contoller."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        session: ClientSession | None = None,
        api_version: str = "v1",
    ) -> None:
        """Initialize the MasterthermController.

        Original call will work with username, password, session and api_version, all are optional, if
        to support the new version have added additional parameters and made all optional,
        if parameter is entered will validate all requried.

        Args:
            username: The mastertherm login username
            password: The mastertherm login password
            session: An aiohttp Client Session
            api_version: The version of the API, mainly the host
                "v1"  : Original version, data response in varfile_mt1_config1
                "v1b" : Original version, datalast_info_update response in varfile_mt1_config2
                "v2"  : New version since 2022 response in varFileData
        Returns:
            The MasterthermController object

        Raises:
            MasterthermUnsupportedVersion: API Version is not supported.

        """
        self._api: MasterthermAPI | None = None
        self._modbus: MasterthermModbus | None = None

        # Initialize Values:
        self._api_configured = False
        self._modbus_configured = False

        # Check we have all parameters.
        if username:
            if not (password and session):
                raise ValueError(
                    "Provide username, password and session together or no parameters."
                )
            else:
                self._api_configured = True

        # The device structure is held as a dictionary with the following format:
        # {
        #   "module_id_unit_id": {
        #       "last_data_update": <datetime>,
        #       "last_info_update": <datetime>,
        #       "last_full_load": <datetime>,
        #       "last_update_time": "1192282722"
        #       "info": { Various Information },
        #       "data": { Normalized Data Information },
        #       "api_info": { All Info retrieved from the API },
        #       "api_update_data": { All Updated Data since last update },
        #       "api_full_data": { Full Data including last updated },
        #   }
        # }
        self.__devices = {}

    async def enable_api(
        self,
        username: str,
        password: str,
        session: ClientSession,
        api_version: str = "v1",
    ) -> bool:
        """Enable the API Interface.

        For API Provide username, password, session, api_version.

        Args:
            username: The mastertherm login username
            password: The mastertherm login password
            session: An aiohttp Client Session
            api_version: The version of the API, mainly the host
                "v1"  : Original version, data response in varfile_mt1_config1
                "v1b" : Original version, datalast_info_update response in varfile_mt1_config2
                "v2"  : New version since 2022 response in varFileData

        Returns:
            The MasterthermController object

        Raises:
            MasterthermUnsupportedVersion: API Version is not supported.

        """
        self._api_configured = True
        return True

    async def enable_modbus(self, modbus_addr: str, hp_type: str | None = None) -> bool:
        """Enable the Modbus IP Interface.

        Provide the details for local connect, requires static IP on heatpump.

        Args:
            modbus_addr: The Modbus IP Address
            hp_type: str: The HeatPump Type, known types:
                "pco5" : Older HP Type Before 2022
                "uPC" : Newer After 2022
        Returns:
            The MasterthermController object

        Raises:
            MasterthermUnsupportedType: Heat Pump Type is not supported.

        """
        self._modbus_configured = True
        return True

    async def connect(self, reload_modules: bool = False) -> bool:
        """Connect to the API, check the supported roles and update if required.

        Args:
            reload_modules: Optional, default False, True to reload modules.

        Returns:
            connected (bool): True if connected Raises Error if not

        Raises:
            MasterthermConnectionError: Failed to Connect
            MasterthermAuthenticationError: Failed to Authenticate
            MasterthermUnsportedRole: Role is not supported by API
            MasterthermServerTimeoutError: Server Timed Out more than once.

        """
        return True
