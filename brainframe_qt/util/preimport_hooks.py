"""This file handles any import hackery that changes the way future modules are
imported. This file should be imported very early in program execution.
"""
import importlib
import logging
import os
import sys

from brainframe.shared.gstreamer import gi_select_versions

# PyInstaller changes sys.path[0] to be zip path, we really want sys.path[1]
sys.path = [sys.path[1]] + [sys.path[0]] + sys.path[2:]


def import_from_path(module_path, module_name):
    """Import a module by name from a specified path.

    Adds the path to syspath, imports the module by name, and then removes the
    path from syspath. This works because imports are singletons, so if this
    is done at the start of the program, all future imports of the module
    will be using the new path
    """
    old_path = sys.path

    try:
        sys.path = [module_path] + old_path

        # Now import the module
        return importlib.import_module(module_name)
    finally:
        sys.path = old_path


# If the user has specified a custom path for PyGObject to be imported from,
# import from that location. This is necessary because PyGObject is an LGPL
# library

pygobject_path = os.environ.get("PYGOBJECT_PATH", None)
if pygobject_path:
    logging.warning(f"Custom PyGObject resource dir specified: "
                    f"{pygobject_path}")
    gi = import_from_path(pygobject_path, "gi")

    gi_select_versions(gi)

    gi_libraries = [
        "gi.repository.GObject",
        "gi.repository.Gst",
        "gi.repository.GstApp",
        "gi.repository.GstRtsp",
        "gi.repository.GstRtspServer",
        "gi.repository.GLib",
        "gi.repository.GstPbutils"
    ]
    for lib in gi_libraries:
        import_from_path(pygobject_path, lib)
else:
    import gi

    gi_select_versions(gi)

# If the user has specified a custom path for argh to be imported from, import
# from that location. This is necessary because argh is an LGPL library.
argh_path = os.environ.get("ARGH_PATH", None)
if argh_path:
    logging.warning(f"Custom argh resource dir specified: "
                    f"{argh_path}")
    argh = import_from_path(argh_path, "argh")

# If the user has specified a custom path for chardet to be imported from,
# import from that location. This is necessary because chardet is an LGPL
# library.
chardet_path = os.environ.get("CHARDET_PATH", None)
if chardet_path:
    logging.warning(f"Custom chardet resource dir specified: "
                    f"{chardet_path}")
    chardet = import_from_path(chardet_path, "chardet")
