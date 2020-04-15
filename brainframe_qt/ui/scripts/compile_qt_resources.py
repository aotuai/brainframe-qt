from pathlib import Path

import pyqt5ac

RESOURCE_DIR = Path("resources")

# noinspection SpellCheckingInspection
PYQT5AC_CONFIG_FILE = RESOURCE_DIR / "qt_resources.yml"
pyqt5ac.main(config=str(PYQT5AC_CONFIG_FILE))
