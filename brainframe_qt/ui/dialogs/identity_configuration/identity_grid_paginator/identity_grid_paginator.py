from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget

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

        # Stores total number of identities that are to be loading. Also used
        # as a check to see if we're known to be uploading
        self._to_upload = 0

        self.container_layout = IdentityGridLayout()

    def add_item(self, identity: Identity):

        # Don't add any more widgets if page is already full
        # noinspection PyPropertyAccess
        page_size = self.page_size
        if self.container_layout.count() >= page_size:
            return

        self._create_identity_entry(identity)

    def clear_layout(self):
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

            for identity in identities:
                self.add_item(identity)
            self.total_items = total_count
            self.next_page_button.setDisabled(
                self.range_upper >= self.total_items)
            self.range_upper_label.setText(str(self.range_upper))

        QTAsyncWorker(self, func, callback).start()

    @pyqtSlot(object)
    def delete_identity_slot(self, identity: Identity):
        """Called when we want to delete an Identity from the database

        Connected to:
        - IdentityEntry --> Dynamic
        [child].identity_delete_signal
        """

        def func():
            api.delete_identity(identity.id)

        def callback(_):
            self.display_page(self.current_page)

        QTAsyncWorker(self, func, callback).start()

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

    def _create_identity_entry(self, identity: Identity):
        identity_entry: QWidget = IdentityEntry(identity, self)
        identity_entry.identity_clicked_signal.connect(
            self.identity_clicked_signal)
        identity_entry.identity_delete_signal.connect(
            self.delete_identity_slot)

        self.add_widget(identity_entry)
        self.range_upper_label.setText(str(self.range_upper))
