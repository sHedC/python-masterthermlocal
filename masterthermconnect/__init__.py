"""Python API wrapper for Mastertherm Connect."""

from masterthermconnect.__version__ import __version__
from masterthermconnect.controller import MasterthermController

__all__ = ["__version__", "MasterthermController"]
