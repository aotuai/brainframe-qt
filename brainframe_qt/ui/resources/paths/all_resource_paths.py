"""This module creates a list of all paths that exist, and returns the correct
path for a file depending on whether or not the script is running inside of
pyinstaller, or as normal python."""
import sys
from typing import Union
from pathlib import Path

all_paths = []
"""A list of all paths in the program. This is used for building the project
to make sure that all used resources get packaged into the executable"""


def _running_in_build() -> bool:
    return hasattr(sys, '_MEIPASS')


def route_path(*args: Union[str, Path]) -> Path:
    """This function takes a path, and routes it to the correct path based on
    whether the client is running from source or in a build.

    :returns: The Path object relative to the build path or source path.
    """
    if _running_in_build():
        return Path(sys._MEIPASS, *args)
    return Path(*args)


def register_path(*args: Union[str, Path]) -> Path:
    """ This function takes a path, routes it, records it for use in
    pyinstaller builds, and returns a pathlib Path object

    :raises FileNotFoundError: If the file/directory doesn't exist
    :returns: The routed (and verified as existing) Path
    """
    if _running_in_build():
        return route_path(*args)

    global all_paths

    # Check if this is a static file to be packaged by Pyinstaller
    path = Path(*args)
    if path.is_file():
        all_paths.append(str(path))

    if not path.exists():
        raise FileNotFoundError(f"Could not find file or directory {path}")
    return path
