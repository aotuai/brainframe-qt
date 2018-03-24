from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

from ui.resources import client_paths


class StreamConfiguration(QDialog):

    def __init__(self):

        super().__init__()

        loadUi(client_paths.stream_configuration_ui, self)