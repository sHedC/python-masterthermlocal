"""Main Program, for Testing Mainly."""

import argparse
import sys

import masterthermconnect.__version__ as __version__


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
            "DO NOT RUN THIS TOO FREQENTLY, IT IS POSSIBLE TO GET YOUR IP BLOCKED, "
            "I think new new API is sensitive to logging in too frequently."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Mastertherm Connect CLI Version: {__version__}",
        help="Show the version of the Mastertherm Connect CLI.",
    )

    return parser.parse_args(argv)


def main(argv=None) -> int:
    """Mastertherm Connect CLI."""
    try:
        args: argparse.Namespace = get_arguments(argv)
    except SystemExit:
        return -1

    return 0


if __name__ == "__main__":
    sys.exit(main())
