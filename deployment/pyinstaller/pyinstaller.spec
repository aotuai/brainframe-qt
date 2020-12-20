# -*- mode: python -*-

import logging
import os
import sys
from pathlib import Path

import pkg_resources
from PyInstaller.utils.hooks import collect_submodules

from brainframe_qt.ui.resources.paths.all_resource_paths import all_paths
from deployment.utils import gstreamer
from deployment.utils.library_licensing import is_banned_library, \
    is_external_library, check_for_unused_library_matchers

# Patch an issue in PyInstaller on Msys2 that causes a mix of backslashes
# and forwardslashes, that leads to "SecurityErrors" which fail the build.
# Tracking issue: https://github.com/pyinstaller/pyinstaller/issues/4402
if sys.platform == "win32":
    import PyInstaller

    get_module_file_attribute = PyInstaller.utils.hooks.get_module_file_attribute


    def patched_get_attr(package):
        attr = get_module_file_attribute(package)
        return attr.replace("\\", "/")


    PyInstaller.utils.hooks.get_module_file_attribute = patched_get_attr

# Tell pyinstaller to package all of the client resources (eg icons, licenses)
data_files = []
for file in all_paths:
    file = Path(file)
    assert file.is_file() and not file.is_absolute()
    data_files.append((str(file.absolute()), str(file.parent)))

# Get ALL python modules, since QT randomly imports them and PyInstaller
# doesn't know about it
all_python_modules = []
for root, subdirs, files in os.walk("./brainframe_qt/"):
    # Get all *.py files and convert them to the python module import format
    files = [os.path.join(root, f)[:-3] for f in files if ".py" == f[-3:]]
    modules = [f[2:].replace('/', '.') for f in files]
    all_python_modules += modules

# Add pkg_resources, as new versions of setuptools depend on it, but
# PyInstaller can't detect that.
# https://github.com/pypa/setuptools/issues/1963
all_python_modules.extend(collect_submodules('pkg_resources'))

# Run build
a = Analysis(
    ["../../../brainframe_client.py"],  # Relative to this file
    binaries=gstreamer.get_libs(),
    datas=data_files,
    hiddenimports=all_python_modules,
    hookspath=[],
    runtime_hooks=[],
    excludes=["pyqt4", "PyQt4", "PyQt5.QtQuickWidgets", "lib2to3"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False)

# Filter out library files with licensing issues
ok_binaries = []
unknown_binaries = []
for binary in a.binaries:
    filename, path, type_ = binary

    path = Path(path)
    if is_external_library(path):
        ok_binaries.append(binary)
    elif is_banned_library(path):
        logging.info(f"Excluding library (bad license): {path}")
    else:
        unknown_binaries.append(str(path))
if len(unknown_binaries):
    names = ", \t\n".join(unknown_binaries)
    raise RuntimeError(f"Unrecognized libraries:\n"
                       f"{names}\n"
                       f"Please check these library's licenses and add them to "
                       f"the proper library lists.")
check_for_unused_library_matchers()

"""
There is a bug where certain 'datas' are trying to be copied 
 to an absolute path. An example is 
>>>    ('C:/tools/msys64/mingw64/lib/python3.7/lib2to3/Grammar.txt', 
...     'C:/tools/msys64/mingw64/lib/python3.7/lib2to3/Grammar.txt', 
...     'DATA')
Where the data[0] is supposed to be a relative path within the executable 
however Analysis is somehow pulling a full path. I try to compensate for this 
bug by removing all offending files. Currently on windows there are none, and
on linux there is 1.
"""
filtered_datas = [d for d in a.datas if not Path(d[0]).is_absolute()]
bad_datas = set(a.datas) - set(filtered_datas)
if len(bad_datas):
    logging.warning("WARNING! The following data files tried to store a file "
                    f"outside of the dist directory: {bad_datas}. If you "
                    f"are having issues with the packaged binary, "
                    f"this may be the cause.")

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    name='BrainFrameClient',
    exclude_binaries=True,
    bootloader_ignore_signals=False,
    debug=False,
    console=True,
    strip=False,
    upx=True)

version_tag = pkg_resources.get_distribution('brainframe-qt').version
directory_name = f"{version_tag.replace('.', '_')}_brainframe_windows_client" \
    if sys.platform == "win32" else "lib"

coll = COLLECT(
    exe,
    ok_binaries,
    a.zipfiles,
    filtered_datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=directory_name)
