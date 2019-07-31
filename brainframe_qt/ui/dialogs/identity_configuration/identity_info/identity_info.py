from collections import defaultdict
from typing import Dict, List

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QMetaObject, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.api.codecs import Identity, Encoding
from brainframe.client.ui.resources import QTAsyncWorker
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
            self.display_identity_slot(identity)

    @pyqtSlot(str)
    def delete_encoding_class_slot(self, encoding_class: str):
        """Delete all encodings of the encoding class type from the identity

        Connected to:
        - EncodingList --> QtDesigner
          [child].delete_encoding_class_signal
        """

        # Make sure that user actually wants to delete the entire class
        if not self._prompt_encoding_class_deletion(encoding_class):
            return

        def func():
            api.delete_encodings(identity_id=self.identity.id,
                                 class_name=encoding_class)

        def callback(_):
            def func2():
                return api.get_identity(self.identity.id)

            def callback2(identity: Identity):
                # Call the slot, but from the correct (UI) thread
                QMetaObject.invokeMethod(
                    self, "display_identity_slot",
                    Qt.QueuedConnection,
                    QtCore.Q_ARG("PyQt_PyObject", identity))

            # Refresh the identity
            QTAsyncWorker(self, func2, callback2).start()

        QTAsyncWorker(self, func, callback).start()

    @pyqtSlot(object)
    def display_identity_slot(self, identity: Identity):
        """Called to display the information for the specified identity

        If identity == None, the widget is hidden

        Connected to:
        - IdentityGridPaginator --> QtDesigner
          [peer].identity_clicked_signal
        """
        if identity is None:
            self.hide()
            return

        self.identity = identity

        self.unique_name.setText(self.tr("Unique Name: {}", "After setting")
                                 .format(identity.unique_name))
        self.nickname.setText(self.tr("Nickname: {}", "After setting")
                              .format(identity.nickname))

        encodings_codecs = api.get_encodings(identity_id=identity.id)
        encodings: Dict[str, List[Encoding]] = defaultdict(list)
        for encoding_codec in encodings_codecs:
            encodings[encoding_codec.class_name].append(encoding_codec)

        encoding_class_names = [k for k in encodings.keys()
                                if k != 'default_factory']
        self.encoding_list.init_encodings(encoding_class_names)

        self.show()

    # noinspection DuplicatedCode
    def _prompt_encoding_class_deletion(self, encoding_class: str) -> bool:
        message = self.tr("Are you sure you want to delete all encodings with "
                          "class {} from identity for {}?") \
            .format(encoding_class, self.identity.unique_name)
        info_text = self.tr("This operation cannot be undone.")

        message_box = QMessageBox(self)
        message_box.setText(message)
        message_box.setInformativeText(info_text)
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Abort)
        message_box.setDefaultButton(QMessageBox.Abort)

        return message_box.exec_() == QMessageBox.Yes
