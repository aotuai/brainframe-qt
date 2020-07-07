from typing import List

import typing
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.uic import loadUi

from brainframe.client.api_utils import api
from brainframe.api.bf_codecs import Capsule
from brainframe.client.ui.resources import QTAsyncWorker
from brainframe.client.ui.resources.paths import qt_ui_paths

from .capsule_list_item.capsule_list_item import CapsuleListItem


class CapsuleList(QListWidget):
    capsule_selection_changed = pyqtSignal(str)
    """This is activated when the user changes the selected capsule in the
    list.

    Connected to:
    - CapsuleConfigDialog -- QtDesigner
      [peer].on_capsule_change
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.capsule_list_ui, self)
        self.current_capsule = None

        # noinspection PyUnresolvedReferences
        self.currentItemChanged.connect(self.capsule_changed)

        self._init_capsules()

    def _init_capsules(self):
        """Populate capsule container layout with those capsules"""

        def get_capsules():
            return api.get_capsules()

        def add_capsules(capsules: List[Capsule]):

            for capsule in capsules:
                capsule_item = QListWidgetItem(parent=self)
                self.addItem(capsule_item)

                item_widget = CapsuleListItem(name=capsule.name, parent=self)

                # Fix sizing
                capsule_item.setSizeHint(item_widget.sizeHint())
                self.setItemWidget(capsule_item, item_widget)

            # Always have an item selected
            if capsules:
                self.setCurrentRow(0)

        QTAsyncWorker(self, get_capsules, on_success=add_capsules).start()

    def capsule_changed(self, current: QListWidgetItem,
                        _previous: QListWidgetItem):
        """When an item on the QListWidget is selected, emit a signal with
        the capsule name as the argument

        Connected to:
        - CapsuleList -- Dynamic
          self.currentItemChanged
        """
        capsule_list_item = typing.cast(CapsuleListItem,
                                        self.itemWidget(current))
        self.current_capsule = capsule_list_item.capsule_name
        # noinspection PyUnresolvedReferences
        self.capsule_selection_changed.emit(self.current_capsule)
