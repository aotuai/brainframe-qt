from typing import List

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimerEvent

from brainframe.client.api import api
from brainframe.client.api.codecs import Identity
from brainframe.client.ui.resources import QTAsyncWorker
from brainframe.client.ui.resources.ui_elements.containers import Paginator

from .identity_entry import IdentityEntry
from .identity_grid_layout import IdentityGridLayout


class IdentityGridPaginator(Paginator):
    identity_clicked_signal = pyqtSignal(object)
    """Emitted when child IdentityGrid has an identity that is clicked
    
    Connected to:
    - IdentityEntry --> Dynamic
      [child].identity_clicked_signal
    - IdentityInfo <-- QtDesigner
      [peer].display_identity_slot
    """
    add_new_identity_slot = pyqtSignal(object)
    """Emitted when child IdentityGrid has an identity that is clicked
    
    Connected to:
    - IdentityGrid --> Dynamic
      self.identity_grid.identity_clicked_signal
    - IdentityInfo <-- QtDesigner
      [peer].display_identity_slot
    """
    identity_load_started_signal = pyqtSignal()
    """Emits when identities are loading

    Connected to:
    - IdentityConfiguration <-- Dynamic
      [parent].[lambda]
    """
    identity_load_progress_signal = pyqtSignal(int, int)
    """Emits percent of identities that have been uploaded so far

    Connected to:
    - IdentityConfiguration <-- Dynamic
      [parent].[lambda]
    """
    identity_load_finished_signal = pyqtSignal()
    """Emits when identities are done loading

    Connected to:
    - IdentityConfiguration <-- Dynamic
      [parent].[lambda]
    """

    def __init__(self, parent=None):
        super().__init__(page_size=200, parent=parent)

        self.search_string: str = None
        self.encoding_class: str = None

        self._identities_to_add: List[Identity] = []
        # Stores total number of identities that are to be loading. Also used
        # as a check to see if we're known to be uploading
        self._to_upload = 0

        self.container_layout = IdentityGridLayout()
        self.startTimer(0)

    def add_item(self, identity: Identity):

        identity_entry = IdentityEntry(identity, self)
        identity_entry.identity_clicked_signal.connect(
            self.identity_clicked_signal)
        self.add_widget(identity_entry)

        self.range_upper_label.setText(str(self.range_upper))

    def clear_layout(self):
        self._identities_to_add.clear()
        # noinspection PyUnresolvedReferences
        self.identity_load_finished_signal.emit()

        for index in reversed(range(self.container_layout.count())):
            widget = self.container_layout.takeAt(index).widget()
            widget.deleteLater()

    def display_page(self, page: int):

        self.clear_layout()

        def func():
            # noinspection PyPropertyAccess
            page_size = self.page_size

            identities, total_count = api.get_identities(
                encoded_for_class=self.encoding_class,
                search=self.search_string,
                limit=page_size,
                offset=page_size * page
            )

            return identities, total_count

        def callback(args):
            identities, total_count = args

            self.add_new_identities_slot(identities)
            self.total_items = total_count
            self.next_page_button.setDisabled(
                self.range_upper >= self.total_items)

        QTAsyncWorker(self, func, callback).start()

    def timerEvent(self, timer_event: QTimerEvent):
        if not self._identities_to_add:
            return

        # Signal start of loading
        if self._to_upload == 0:
            self._to_upload = len(self._identities_to_add)
            # noinspection PyUnresolvedReferences
            self.identity_load_started_signal.emit()

        identity = self._identities_to_add.pop()

        # Don't add any more widgets if page is already full
        # noinspection PyPropertyAccess
        page_size = self.page_size
        if self.container_layout.count() >= page_size:
            return

        self.add_item(identity)

        # Signal load progress
        uploaded_so_far = self._to_upload - len(self._identities_to_add)
        # noinspection PyUnresolvedReferences
        self.identity_load_progress_signal.emit(
            uploaded_so_far, self._to_upload)

        # Signal end of uploading
        if not self._identities_to_add:
            self._to_upload = 0
            # noinspection PyUnresolvedReferences
            self.identity_load_finished_signal.emit()

    # Not using a simple property so that Qt can use it as a slot
    @pyqtSlot(str)
    def set_search_string(self, search_string: str):
        # Empty string results in no filtering
        self.search_string = search_string or None
        self.display_page(0)

    # Not using a simple property so that Qt can use it as a slot
    @pyqtSlot(str)
    def set_encoding_class(self, encoding_class: str):
        # Empty string results in no filtering
        self.encoding_class = encoding_class or None
        self.display_page(0)

    # noinspection PyPropertyAccess
    @pyqtSlot(object)
    def add_new_identities_slot(self, identities: List[Identity]):
        """Called when we want to dynamically add a new identities to the grid

        Connected to:
        - IdentityConfiguration --> QtDesigner
          [parent].display_new_identity_signal
        """
        if not isinstance(identities, list):
            identities = [identities]
        if self.container_layout.count() + 1 < self.page_size:
            self._identities_to_add.extend(identities)
