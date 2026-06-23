#!/usr/bin/env python3
# Import hack for LGPL compliance. This runs stuff on import
# noinspection PyUnresolvedReferences
from brainframe_qt.util import preimport_hooks

import argparse
import faulthandler
import os
import sys

from brainframe_qt.ui.brainframe_app import BrainFrameApplication
from brainframe_qt.util import environment


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--latency", type=int, default=50, help="Stream jitter buffer latency in milliseconds")
    args, _ = parser.parse_known_args(sys.argv)
    os.environ["BF_STREAM_LATENCY"] = str(args.latency)

    faulthandler.enable()

    environment.set_up_environment()

    # Run the UI
    app = BrainFrameApplication()
    app.exec()


if __name__ == '__main__':
    main()
