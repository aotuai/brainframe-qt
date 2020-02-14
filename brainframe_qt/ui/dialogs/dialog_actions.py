import logging
import os

from PyQt5.QtWidgets import QApplication


def close_client():
    logging.info(QApplication.translate("StandardError", "Quitting"))

    # TODO: Why does QApplication.exit not work
    QApplication.exit(-1)

    # TODO: Should not be necessary but QApplication.exit doesn't work
    # noinspection PyProtectedMember
    os._exit(-1)
