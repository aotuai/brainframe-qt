"""Provides utilities for including GStreamer items inside of PyInstaller
builds. This is necessary because GStreamer does a lot of runtime linking that
PyInstaller cannot detect.
"""

import sys
from pathlib import Path


def platform_path(linux, win32):
    if sys.platform == "linux":
        path = Path(linux)
    elif sys.platform == "win32":
        path = Path(win32)
    else:
        raise SystemError(f"Unknown sys.platform type of {sys.platform}")
    assert path is not None and path.exists(), \
        f"Could not find path {path} for platform {sys.platform}"
    return path


GST_LIB_PATH = platform_path(
    linux="/usr/local/lib/x86_64-linux-gnu/",
    win32="C:/tools/msys64/mingw64/lib/")
"""The place where GStreamer core libraries are installed."""

GST_PLUGIN_PATHS = [
    platform_path(linux="/usr/local/lib/x86_64-linux-gnu/gstreamer-1.0",
                  win32="C:/tools/msys64/mingw64/lib/gstreamer-1.0/")]
"""The place where GStreamer plugins are installed."""

VA_API_DRIVER_PATH = Path("/usr/local/lib/dri")

GMMLIB_PATH = Path("/usr/local/lib/libigdgmm.so.11")

GST_REPOSITORY_PATH = platform_path(
    linux="/usr/lib/x86_64-linux-gnu/girepository-1.0/",
    win32="C:/tools/msys64/mingw64/lib/girepository-1.0/")
"""The place where all the *.typelib files are, such as Gst-1.0.typelib"""

GST_PLUGIN_BLACKLIST = [
    # aasink: A sink that lets you watch videos in a terminal. Really cool but
    #         not useful for us.
    "libgstaasink.*",
    # jack: We don't need specific support for the Jack audio interface
    "libgstjack.*",
]
"""A list of plugin names that should not be included in the release
because they aren't useful to us.
"""


def get_libs():
    """
    :return: List of GStreamer libraries and plugins in PyInstaller's TOC format
    """
    gst_binaries = []
    for lib in GST_LIB_PATH.glob("libgst*.*"):
        gst_binaries.append((str(lib), "."))

    # Add all LGPL licensed plugins that are not blacklisted
    for plugin_path in GST_PLUGIN_PATHS:
        for plugin in plugin_path.glob("*.*"):  # All *.so's and *.dll's
            blacklisted = any(str(plugin.name) == name
                              for name in GST_PLUGIN_BLACKLIST)
            if not blacklisted:
                gst_binaries.append((str(plugin), "gst_plugins/."))

    # Add all typelib files
    for typelib in GST_REPOSITORY_PATH.glob("*.typelib"):
        gst_binaries.append((str(typelib), "gi_typelibs/."))

    # Add all VA-API drivers, if we're on Linux. Sorry Windows users.
    if sys.platform == "linux":
        for driver_path in VA_API_DRIVER_PATH.glob("*.so"):
            gst_binaries.append((str(driver_path), "dri/."))

        # iHD depends on this library
        assert GMMLIB_PATH.is_file(), "The gmmlib library is missing!"
        gst_binaries.append((str(GMMLIB_PATH), "."))

    return list(set(gst_binaries))
