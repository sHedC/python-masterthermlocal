"""Main Program, for Testing Mainly."""

import argparse
import asyncio
import configparser
import logging
import sys

from aiohttp import ClientSession, ClientTimeout

from masterthermconnect import MasterthermController, __version__
from masterthermconnect.api import MasterthermAPI
from masterthermconnect.exceptions import MasterthermError
from masterthermconnect.modbus import MasterthermModbus

_LOGGER: logging.Logger = logging.getLogger(__name__)


class MasterthermCLIShell:
    """Mastertherm Connect CLI Shell."""

    def __init__(self) -> None:
        """Initialise the Mastertherm Connect CLI Shell."""
        self._config_file: str = "masterthermconnect.cfg"
        self._controller: MasterthermController = MasterthermController()
        self._configured = False

        self._api_configured: bool = False
        self._api_connected: bool = False
        self._local_configured: bool = False
        self._local_connected: bool = False

        self._api_version: str | None = None
        self._username: str | None = None
        self._password: str | None = None
        self._local_ip: str | None = None
        self._hp_type: str | None = None

    def _input(self, message: str, answers_allowed: list[str]) -> str:
        """As for input, make sure the answer is valid."""
        answer: str = input(message)
        while not answers_allowed or answer.lower() not in answers_allowed:
            answer = input(message)

        return answer.lower()

    async def _setup_api(self) -> bool:
        """Connect to the Mastertherm API."""
        if not self._api_configured:
            raise ValueError("API not configured. Please run 'config' first.")

        if (
            self._api_version is None
            or self._username is None
            or self._password is None
        ):
            raise ValueError("API configuration incomplete.")

        session = ClientSession(timeout=ClientTimeout(total=10))
        success = False
        try:
            self._api = MasterthermAPI(
                self._username,
                self._password,
                session=session,
                api_version=self._api_version,
            )
            # await self._api.connect()
        except MasterthermError as mte:
            _LOGGER.error("Error %s", mte.message)

        return success

    async def get_command(
        self, login_user: str, login_pass: str, args: list[str]
    ) -> int:
        """Get Command to get data/ registry/ devices."""
        modbus = MasterthermModbus("172.16.46.100", "mt_0")
        await modbus.connect()

        result = await modbus.get_registers(1)
        _LOGGER.warning("Result: %s", result)

        modbus.close()
        return 0

    async def load_config(self) -> int:
        """Load configuration from a file."""
        config = configparser.ConfigParser()
        config.read(self._config_file)

        # Check if there is a setup to load, if not, return -1
        if "SETUP" not in config:
            _LOGGER.error("Configuration not set, please use config to setup.")
            return -1

        self._api_configured = config.getboolean(
            "SETUP", "Api_Configure", fallback=False
        )
        self._local_configured = config.getboolean(
            "SETUP", "Local_Configure", fallback=False
        )

        # Load the API configuration if configured
        if self._api_configured:
            self._api_version = config.get("API", "api_version", fallback=None)
            self._username = config.get("API", "username", fallback=None)
            self._hp_type = config.get("API", "hp_type", fallback=None)

            #   Check Login and Lookup HP Type
            self._api_connected = False
            if await self._setup_api():
                self._api_connected = True

        # Load the local configuration if configured
        if self._local_configured:
            self._local_ip = config.get("LOCAL", "local_ip", fallback=None)
            self._hp_type = config.get("LOCAL", "hp_type", fallback=None)

        # If Password is not passed, ask for it.
        if self._password is None:
            self._password = input("Enter your login password: ")

        return 0

    async def configure(self, args: list[str] = []) -> None:
        """Configure the Mastertherm Connect CLI Shell."""
        if (
            self._configured
            and input(
                "Already configured. Do you wish to re-configure? (y/n): "
            ).lower()
            != "y"
        ):
            _LOGGER.info("Configuration skipped.")
        else:
            _LOGGER.info("Configuring Mastertherm Connect CLI Shell.")

            # Ask if we want to configure the online API
            if (
                self._input(
                    "Do you wish to configure the online API? (y/n): ", ["y", "n"]
                )
                == "y"
            ):
                self._api_configured = True

                if (
                    self._input(
                        "Which version of the App do you use?\n"
                        "  1. MasterTherm App, mastertherm.vip-it.cz (< 2022)\n"
                        "  2. MasterTherm Touch App, mastertherm.online (> 2022)\n"
                        "  Enter 1 or 2: ",
                        ["1", "2"],
                    )
                    == "1"
                ):
                    self._api_version = "v1"
                else:
                    self._api_version = "v2"

                self._username = input("Enter your login username: ")
                self._password = input("Enter your login password: ")

                #   Setup and Connect API

            # Ask for Local IP.
            if (
                self._input("Do you wish to configure a local IP? (y/n): ", ["y", "n"])
                == "y"
            ):
                self._local_configured = True
                self._local_ip = input("Enter the local IP address of your heat pump: ")
                if self._hp_type is None:
                    hp_type = self._input(
                        "The HP Controller type can be found in the App under Info: \n"
                        "  1. Controller: pco5, Exp: 0\n"
                        "  2. Controller uPC, Exp: 0\n"
                        "  Select 1 or 2: ",
                        ["1", "2"],
                    )
                    self._hp_type = "pco5_0" if hp_type == "1" else "uPC_0"

            # Ask to save configuration
            if (
                self._input(
                    "Do you wish to save the configuration? (y/n): ", ["y", "n"]
                )
                == "y"
            ):
                # Here we would save the configuration to a file or database
                config = configparser.ConfigParser()

                config.add_section("SETUP")
                config.set("SETUP", "configured", "true")
                config.set("SETUP", "Api_Configure", str(self._api_configured))
                config.set("SETUP", "Local_Configure", str(self._local_configured))

                if self._api_configured:
                    config.add_section("API")
                    config.set("API", "api_version", self._api_version)
                    config.set("API", "username", self._username)
                    config.set("API", "hp_type", self._hp_type)

                if self._local_configured:
                    config.add_section("LOCAL")
                    config.set("LOCAL", "local_ip", self._local_ip)
                    config.set("LOCAL", "hp_type", self._hp_type)

                with open(self._config_file, "w") as configfile:
                    config.write(configfile)

                _LOGGER.info("Configuration saved.")

            self._configured = True
            _LOGGER.info("Configuration complete.")

    async def process_command(self, command: str, args: list[str]) -> int:
        """Process a command entered in the shell."""
        # Configure local IP, Login URL, User, Password, HP Type
        # maybe config then a question/ answer, config save and config load?

        match command:
            case "config":
                await self.configure(args)
            case "get":
                if self._configured:
                    _LOGGER.info("Config command not implemented yet.")
                else:
                    _LOGGER.error("Not configured yet. Please run 'config' first.")
            case _:
                _LOGGER.error("Unknown command: %s", command)

        return 0

    async def start(
        self,
        config_file: str = "masterthermconnect.cfg",
        password: str = "",
    ) -> None:
        """Run the CLI shell."""
        _LOGGER.info(
            "Entering Mastertherm Connect CLI Shell. Type 'help' for commands.\n"
        )
        self._config_file = config_file
        if password != "":
            self._password = password

        if await self.load_config() == -1:
            await self.configure([])

        while True:
            command = input("$> ")
            if command == "exit":
                break
            elif command.startswith("help"):
                self.display_help(command)
            else:
                items: list[str] = command.split(" ")
                await self.process_command(items[0], items[1:])

    def display_help(self, help_args: str) -> None:
        """Display help information."""
        _LOGGER.info(
            "Mastertherm Connect CLI tester, Shell Available Commands:\n"
            "  - help: Display this help message\n"
            "  - config: Configure the Mastertherm Connect CLI Shell\n"
            "  - exit: Exit the shell\n"
        )


def get_arguments(argv: list[str]) -> argparse.Namespace:
    """Read the Arguments passed in."""
    # formatter_class=argparse.MetavarTypeHelpFormatter,
    parser = argparse.ArgumentParser(
        prog="masterthermconnect",
        description=(
            "Mastertherm Connect CLI Tester, used for debug purposes, "
            "allows you to get and set registers and other information for testing"
        ),
        epilog=(
            "If using the API, please ensure you do not ping the server too often, or you may get your IP blocked."
        ),
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="Mastertherm Connect CLI Tester Version: " + __version__,
        help="display the Mastertherm Connect CLI Tester Version",
    )

    # Sub Commands are get and set:
    subparsers = parser.add_subparsers(
        title="commands",
        description=(
            "Valid commands, use -h to get more help after the command for specific help."
        ),
        help="Retrieve and Send data to or from the API.",
    )

    parser_shell = subparsers.add_parser("shell", help="start the CLI Shell")
    parser_shell.set_defaults(command="shell")
    parser_shell.add_argument(
        "-c", "--config", type=str, help="the configuration file, to use."
    )
    parser_shell.add_argument(
        "-p", "--password", type=str, help="the API login password."
    )

    return parser.parse_args(argv)


def main(argv: list[str]) -> str | int | None:
    """Mastertherm Connect CLI."""
    _LOGGER.setLevel(logging.INFO)
    _LOGGER.addHandler(logging.StreamHandler(sys.stdout))

    # Arg Parse raises SystemExit, get return value
    try:
        args: argparse.Namespace = get_arguments(argv)
    except SystemExit as ex:
        return ex.code

    # Check we have any arguments
    try:
        if not args.command:
            return -1
    except Exception:
        _LOGGER.info("usage: masterthermconnect -h")
        return 0

    if args.command == "shell":
        shell = MasterthermCLIShell()
        if args.config:
            return asyncio.run(
                shell.start(config_file=args.config, password=args.password)
            )
        else:
            return asyncio.run(shell.start(password=args.password))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
