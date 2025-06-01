"""Main Program, for Testing Mainly."""

import argparse
import asyncio
import logging
import sys

import masterthermconnect.__version__ as __version__
from masterthermconnect.modbus import MasterthermModbus

_LOGGER: logging.Logger = logging.getLogger(__name__)


def get_arguments(argv=None) -> argparse.Namespace:
    """Get the command line arguments."""
    parser = argparse.ArgumentParser(
        prog="masterthermconnect",
        description=(
            "Python Mastertherm Connect API Module, used for debug purposes, "
            "allows you to get and set registers and other information for testing, "
            "use with caution!!!"
        ),
        epilog=(
            "There is no protection against updating registers, use this to write with total caution."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Mastertherm Connect CLI Version: {__version__}",
        help="Show the version of the Mastertherm Connect CLI.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="Print debugging statements.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print verbose statements.",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )

    return parser.parse_args(argv)


async def get_command(login_user: str, login_pass: str, args) -> int:
    """Get Command to get data/ registry/ devices."""
    modbus = MasterthermModbus("172.16.46.100", "mt_0")
    await modbus.connect()

    result = await modbus.get_registers(1)
    _LOGGER.warning("Result: %s", result)

    modbus.close()
    return 0


def main(argv=None) -> int:
    """Mastertherm Connect CLI."""
    try:
        args: argparse.Namespace = get_arguments(argv)
    except SystemExit:
        return -1

    return asyncio.run(get_command("login_user", "login_pass", args))


if __name__ == "__main__":
    sys.exit(main())
