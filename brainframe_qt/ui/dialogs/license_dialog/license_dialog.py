from PyQt5.QtWidgets import QListWidgetItem, QWidget

from brainframe.api import bf_codecs
from brainframe.client.api_utils import api
from brainframe.client.ui.resources import QTAsyncWorker
from .license_dialog_ui import _LicenseDialogUI
from .product_sidebar.product_widget import ProductWidget


class LicenseDialog(_LicenseDialogUI):
    BRAINFRAME_PRODUCT_NAME = "BrainFrame"

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

        self._init_products()

    @classmethod
    def show_dialog(cls, parent):
        dialog = cls(parent)

        dialog.resize(900, 500)

        dialog.exec_()

    def _init_signals(self) -> None:
        self.product_sidebar.currentItemChanged.connect(self.change_product)

    def _init_products(self):
        def on_success(license_info: bf_codecs.LicenseInfo):
            icon_path = ":/icons/capsule_toolbar"
            self.product_sidebar.add_product(
                self.BRAINFRAME_PRODUCT_NAME, icon_path, license_info)

            # BrainFrame product should always be first in list
            self.product_sidebar.setCurrentRow(0)

        def on_error():
            pass

        QTAsyncWorker(self, api.get_license_info,
                      on_success=on_success, on_error=on_error) \
            .start()

        # TODO: Also get capsule information if that's ever added

    def change_product(self, item: QListWidgetItem) -> None:
        widget: ProductWidget = self.product_sidebar.itemWidget(item)

        self.license_details.set_product(widget.product_name,
                                         widget.license_info)
