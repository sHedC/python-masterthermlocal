"""Main Program, for Testing Mainly."""

import asyncio
import logging
import sys

from masterthermconnect import __version__
from masterthermconnect.modbus import MasterthermModbus

_LOGGER: logging.Logger = logging.getLogger(__name__)


class MasterthermCLIShell:
    """Mastertherm Connect CLI Shell."""

    def __init__(self) -> None:
        """Initialise the Mastertherm Connect CLI Shell."""
        self._configured = False
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

    async def get_command(self, login_user: str, login_pass: str, args) -> int:
        """Get Command to get data/ registry/ devices."""
        modbus = MasterthermModbus("172.16.46.100", "mt_0")
        await modbus.connect()

        result = await modbus.get_registers(1)
        _LOGGER.warning("Result: %s", result)

        modbus.close()
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

                #   Check Login and Lookup HP Type

            # Ask for Local IP.
            if (
                self._input("Do you wish to configure a local IP? (y/n): ", ["y", "n"])
                == "y"
            ):
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
                _LOGGER.info("Configuration saved.")

            self._configured = True
            _LOGGER.info("Configuration complete.")

    def display_help(self, help_args: str) -> None:
        """Display help information."""
        _LOGGER.info(
            "Mastertherm Connect CLI tester, Shell Available Commands:\n"
            "  - exit: Exit the shell\n"
            "  - help: Display this help message\n"
        )

    async def process_command(self, command: str, args: list[str]) -> int:
        """Process a command entered in the shell."""
        # Configure local IP, Login URL, User, Password, HP Type
        # maybe config then a question/ answer, config save and config load?

        match command:
            case "config" | "cfg" | "configure":
                await self.configure(args)
            case "get":
                if self._configured:
                    _LOGGER.info("Config command not implemented yet.")
                else:
                    _LOGGER.error("Not configured yet. Please run 'config' first.")
            case _:
                _LOGGER.error("Unknown command: %s", command)

        return 0

    async def start(self) -> None:
        """Run the CLI shell."""
        _LOGGER.info(
            "Entering Mastertherm Connect CLI Shell. Type 'help' for commands."
        )
        while True:
            command = input("$> ")
            if command == "exit":
                break
            elif command.startswith("help"):
                self.display_help(command)
            else:
                items: list[str] = command.split(" ")
                await self.process_command(items[0], items[1:])


def main() -> str | int | None:
    """Mastertherm Connect CLI."""
    _LOGGER.setLevel(logging.INFO)
    _LOGGER.addHandler(logging.StreamHandler(sys.stdout))

    # Process Version Argument
    if len(sys.argv) > 1:
        if sys.argv[1] == "-v" or sys.argv[1] == "--version":
            _LOGGER.info("Mastertherm Connect CLI Tester Shell Version %s", __version__)
            return 0
        elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
            _LOGGER.info(
                "Mastertherm Connect CLI Tester Shell Version %s.\n"
                "Run without arguments to enter the shell.",
                __version__,
            )
            return 0
        else:
            _LOGGER.info("Unknown argument: %s", sys.argv[1])
            return 1

    # Start the CLI Shell
    shell = MasterthermCLIShell()
    return asyncio.run(shell.start())


if __name__ == "__main__":
    sys.exit(main())
