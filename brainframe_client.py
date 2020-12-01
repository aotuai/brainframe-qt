# Import hack for LGPL compliance. This runs stuff on import
# noinspection PyUnresolvedReferences
from brainframe_qt.util import preimport_hooks

import faulthandler
import sys

from brainframe_qt.ui.brainframe_app import BrainFrameApplication
from brainframe_qt.util import environment


def main():
    faulthandler.enable()

    environment.set_up_environment()

    # Run the UI
    app = BrainFrameApplication(sys.argv)
    app.exec()


if __name__ == '__main__':
    main()
