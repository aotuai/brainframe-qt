from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.api.codecs import Identity
from brainframe.client.ui.resources.paths import qt_ui_paths

from ..encoding_list import EncodingList


class IdentityInfo(QWidget):
    def __init__(self, parent=None, identity: Identity = None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_info_ui, self)

        self.unique_name: QLabel
        self.nickname: QLabel
        self.encoding_list: EncodingList

        self.identity: Identity = identity

        if not identity:
            return

        self.unique_name.setText(identity.unique_name)
        self.nickname.setText(identity.nickname)

        encodings = api.get_encodings(identity_id=identity.id)
        self.encoding_list.init_encodings(encodings)
