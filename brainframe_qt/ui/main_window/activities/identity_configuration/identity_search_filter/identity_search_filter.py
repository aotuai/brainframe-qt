from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLineEdit, QWidget
from PyQt5.uic import loadUi

from brainframe_qt.api_utils import api
from brainframe_qt.ui.resources import QTAsyncWorker
from brainframe_qt.ui.resources.paths import qt_ui_paths
from brainframe_qt.ui.resources.ui_elements.widgets.dialogs import \
    BrainFrameMessage
from ..encoding_list import EncodingList


class IdentitySearchFilter(QWidget):
    filter_by_encoding_class_signal = pyqtSignal(str)
    """Emitted when it is desired to filter by an encoding class name
    
    Connected to:
    - EncodingList --> QtDesigner
      self.encoding_list.encoding_entry_selected_signal
    - IdentityGrid <-- QtDesigner
      [peer].filter_by_encoding_class_slot
    """
    filter_by_search_string_signal = pyqtSignal(str)
    """Emitted whenever the contents of the search QLineEdit change
    
    Connected to:
    - QLineEdit --> Dynamic
      self.search_line_edit.textChanged
    - IdentityGrid <-- QtDesigner
      [peer].filter_by_search_slot
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_search_filter_ui, self)

        self.encoding_list: EncodingList
        self.search_line_edit: QLineEdit

        self.init_ui()

        self.init_encoding_list()

    def init_ui(self):
        self.search_line_edit.setContentsMargins(10, 5, 10, 5)
        self.encoding_list.setContentsMargins(0, 9, 0, 9)

    def init_encoding_list(self):

        def func():
            capsules = api.get_capsules()

            # Get names of all classes that encodable
            encoding_class_names = set()
            for capsule in capsules:
                output_type = capsule.output_type
                if not output_type.encoded:
                    continue
                encoding_class_names.update(output_type.detections)

            encoding_class_names.update(api.get_encoding_class_names())

            return encoding_class_names

        def callback(encoding_class_names):
            self.encoding_list.init_encodings(encoding_class_names)

        QTAsyncWorker(self, func, on_success=callback).start()

    @pyqtSlot(str)
    def delete_encoding_class_slot(self, encoding_class: str):
        """Delete event encoding of a class type from all identities on the
        database

        Connected to:
        - EncodingList --> Dynamic
          [child].delete_encoding_class_signal
        """

        self.encoding_list: EncodingList

        # Make sure that user actually wants to delete the entire class
        if not self._prompt_encoding_class_deletion(encoding_class):
            return

        def func():
            api.delete_encodings(class_name=encoding_class)

        def callback(_):
            # Refresh the encoding class list. The one we just deleted could be
            # gone if there is no corresponding encoder capsule loaded
            self.init_encoding_list()

            # Tell the grid to not filter by anything anymore
            # noinspection PyUnresolvedReferences
            self.filter_by_encoding_class_signal.emit("")

        QTAsyncWorker(self, func, on_success=callback).start()

    # noinspection DuplicatedCode
    def _prompt_encoding_class_deletion(self, encoding_class: str) -> bool:
        title = self.tr("Are you sure?")
        message = self.tr('Are you sure you want to delete all encodings with '
                          'class "{encoding_class}" from the database?') \
            .format(encoding_class=encoding_class)
        info_text = self.tr("This operation cannot be undone.")

        dialog = BrainFrameMessage.question(
            parent=self,
            title=title,
            question=message,
            subtext=info_text,
            buttons=BrainFrameMessage.PresetButtons.YES
        )

        dialog.add_button(standard_button=BrainFrameMessage.Abort)
        dialog.setDefaultButton(BrainFrameMessage.Abort)

        return dialog.exec() == BrainFrameMessage.Yes
