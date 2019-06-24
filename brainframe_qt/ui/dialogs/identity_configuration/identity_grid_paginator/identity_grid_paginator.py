from typing import List, Tuple

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QScrollArea, QFrame, QSizePolicy

from brainframe.client.api import api
from brainframe.client.api.codecs import Identity
from brainframe.client.ui.resources import QTAsyncWorker
from brainframe.client.ui.resources.ui_elements.containers import Paginator

from .identity_grid import IdentityGrid


class IdentityGridPaginator(Paginator):
    identity_clicked_signal = pyqtSignal(object)
    """Emitted when child IdentityGrid has an identity that is clicked
    
    Connected to:
    - IdentityGrid --> Dynamic
      self.identity_grid.identity_clicked_signal
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

    def __init__(self, parent=None):
        super().__init__(page_size=200, parent=parent)

        self.search_string: str = None
        self.encoding_class: str = None

        self.grid_scroll_area: QScrollArea = None

        self._init_ui()
        self._init_slots_and_signals()

        self.get_page(0)

    def _init_ui(self):
        self.grid_scroll_area = QScrollArea(self)
        self.grid_scroll_area.setFrameShape(QFrame.NoFrame)
        self.grid_scroll_area.setFrameShadow(QFrame.Plain)
        self.grid_scroll_area.setLineWidth(0)
        self.grid_scroll_area.setWidgetResizable(True)

        self.identity_grid = IdentityGrid(self)
        self.identity_grid.setSizePolicy(QSizePolicy.Preferred,
                                         QSizePolicy.Expanding)

        self.grid_scroll_area.setWidget(self.identity_grid)
        self.container_widget = self.grid_scroll_area

    def _init_slots_and_signals(self):
        self.identity_grid.identity_clicked_signal.connect(
            self.identity_clicked_signal)

    def get_page(self, page: int):
        self.identity_grid.clear_identities()

        def func():
            # noinspection PyPropertyAccess
            page_size = self.page_size

            identities = api.get_identities(
                encoded_for_class=self.encoding_class,
                search=self.search_string,
                limit=page_size,
                offset=page_size * page
            )

            return identities

        def callback(identities):
            self.identity_grid.add_identities(identities)

        QTAsyncWorker(self, func, callback).start()

    @pyqtSlot(str)
    def set_search_string(self, search_string: str):
        self.search_string = search_string
        self.get_page(0)

    @pyqtSlot(str)
    def set_encoding_class(self, encoding_class: str):
        self.encoding_class = encoding_class
        self.get_page(0)

    @pyqtSlot(object)
    def add_new_identities_slot(self, *identities):
        """Called when we want to dynamically add a new identities to the grid

        Connected to:
        - IdentityConfiguration --> QtDesigner
          [parent].display_new_identity_signal
        """
        self.identity_grid.add_identities([*identities])
