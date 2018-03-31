# -*- mode: python -*-

import os
from visionapp.shared import dependency_check

assert "visionapp" not in os.getcwd(),\
	"You need to run pyinstaller from the root directory of the project!"

# Make sure dependencies are installed
assert dependency_check.OpenCVDep.ffmpeg, \
        "OpenCV must be compiled with ffmpeg to build this project!"

# Get all the paths required for the project
from visionapp.client.ui.resources.paths import \
	all_resource_paths, image_paths, qt_ui_paths

# Put files in a format that pyinstaller understands
data_files = []
for file in all_resource_paths.all_paths:
    print("Including resource", file)
    data_files.append((file, file, 'DATA'))

# Get ALL python modules, since QT randomly imports them and PyInstaller doesn't know about it
all_python_modules = []
for root, subdirs, files in os.walk("./visionapp/client/"):
	# Get all *.py files and convert them to the python module import format
    files = [os.path.join(root, f)[:-3] for f in files if ".py" == f[-3:]]
    modules = [f[2:].replace('/', '.') for f in files]
    all_python_modules += modules


# Run build
a = Analysis(['../../vision_on_wheels.py'],
             binaries=[],
             datas=[],
             hiddenimports=all_python_modules,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None)


# For a secure build:
pyz = PYZ(a.pure, a.zipped_data, cipher=None)


exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas + data_files,
          name='VisionAppClient',
          debug=False,
          strip=False,
          upx=True,
          console=True )
