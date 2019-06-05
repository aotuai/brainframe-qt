from collections import defaultdict
from typing import Dict, List

from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.api.codecs import Identity, Encoding
from brainframe.client.ui.resources.paths import qt_ui_paths

from ..encoding_list import EncodingList


class IdentityInfo(QWidget):
    def __init__(self, parent=None, identity: Identity = None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_info_ui, self)

        self.unique_name: QLabel
        self.nickname: QLabel
        self.encoding_list: EncodingList

        self.identity: Identity = None

        if identity:
            self.init_identity(identity)

    def init_identity(self, identity):
        self.identity = identity

        self.unique_name.setText(identity.unique_name)
        self.nickname.setText(identity.nickname)

        encodings_codecs = api.get_encodings(identity_id=identity.id)
        encodings: Dict[str, List[Encoding]] = defaultdict(list)
        for encoding_codec in encodings_codecs:
            encodings[encoding_codec.class_name].append(encoding_codec)

        encoding_class_names = [k for k in encodings.keys()
                                if k != 'default_factory']
        self.encoding_list.init_encodings(encoding_class_names)

        self.show()
