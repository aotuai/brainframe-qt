"""This module creates a list of all paths that exist, and returns the correct
path for a file depending on whether or not the script is running inside of
pyinstaller, or as normal python."""
import sys
import os
from typing import Union
from pathlib import Path

all_paths = []
"""A list of all paths in the program. This is used for building the project
to make sure that all used resources get packaged into the executable"""


def _running_in_build() -> bool:
    return hasattr(sys, '_MEIPASS')


def _running_in_snap() -> bool:
    return "SNAP" in os.environ


_RESOURCES_DIR = Path("brainframe/client/ui/resources")
"""The resources directory, relative to the client's root directory"""


def find_client_root() -> Path:
    """Traverses up the directory tree until the client's root installation
    directory is found.

    :return: The client's root installation directory
    """
    # TODO: Replace with
    #       Path(sys.modules['__main__'].__file__).parent
    #       or
    #       import __main__; Path(__main__.__file__).parent
    #       if we stop compiling the client with Cython.
    for parent in Path(__file__).absolute().parents:
        if (parent / _RESOURCES_DIR).is_dir():
            return parent

    raise RuntimeError(f"Could not find the client root installation "
                       f"directory! This can happen if files were left out "
                       f"during packaging or if the resources directory is no "
                       f"longer at {_RESOURCES_DIR}.")


def route_path(*args: Union[str, Path]) -> Path:
    """This function takes a path, and routes it to the correct path based on
    whether the client is running from source or in a build.

    :returns: The Path object relative to the build path or source path.
    """
    if _running_in_build():
        return Path(sys._MEIPASS, *args)
    elif _running_in_snap():
        return Path(find_client_root(), *args)
    return Path(*args)


def register_path(*args: Union[str, Path]) -> Path:
    """ This function takes a path, routes it, records it for use in
    pyinstaller builds, and returns a pathlib Path object

    :raises FileNotFoundError: If the file/directory doesn't exist
    :returns: The routed (and verified as existing) Path
    """
    if _running_in_build() or _running_in_snap():
        return route_path(*args)

    global all_paths

    # Check if this is a static file to be packaged by Pyinstaller
    path = Path(*args)
    if path.is_file():
        all_paths.append(str(path))

    if not path.exists():
        raise FileNotFoundError(f"Could not find file or directory {path}")
    return path
