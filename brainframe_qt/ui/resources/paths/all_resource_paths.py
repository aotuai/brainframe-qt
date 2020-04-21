"""This module creates a list of all paths that exist, and returns the correct
path for a file depending on whether or not the script is running inside of
pyinstaller, or as normal python."""
import sys
from typing import Union
from pathlib import Path

all_paths = []
"""A list of all paths in the program. This is used for building the project
to make sure that all used resources get packaged into the executable"""


def route_path(*args: Union[str, Path]) -> Path:
    """This function takes a path, routes it to the correct spot, records it,
    and returns a pathlib Path object"""
    global all_paths
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS, *args)

    # Check if this file should be saved for pyinstaller
    path = Path(*args)
    if path.is_file():
        all_paths.append(str(path))

    if not path.exists():
        raise FileNotFoundError(f"Could not find file or directory {path}")
    return path
