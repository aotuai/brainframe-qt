from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication, QListWidgetItem
from brainframe.api import bf_errors

from brainframe_qt.ui.resources import QTAsyncWorker
from brainframe_qt.ui.resources.links.documentation import LICENSE_DOCS_LINK
from brainframe_qt.ui.resources.ui_elements.widgets.dialogs import BrainFrameMessage, \
    WorkingIndicator
from brainframe_qt.util.licensing import LicenseInfo, LicenseManager

from .core import licensing
from .core.base import LicensedProduct
from .license_dialog_ui import _LicenseDialogUI
from .widgets import ProductWidget


class LicenseDialog(_LicenseDialogUI):
    BRAINFRAME_PRODUCT_NAME = "BrainFrame"
    BRAINFRAME_PRODUCT_ICON = ":/icons/capsule_toolbar"

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self.license_manager = LicenseManager(parent=self)

        self._init_products()

        self._init_signals()

    @classmethod
    def show_dialog(cls, *, parent: QObject):
        dialog = cls(parent=parent)

        dialog.setWindowTitle(QApplication.translate("LicenseDialog", "Licenses"))
        dialog.resize(900, 500)

        dialog.exec_()

    def _init_signals(self) -> None:
        self.product_sidebar.currentItemChanged.connect(self.change_product)

        self.license_details.license_text_update.connect(self.send_update_license_text)
        self.license_details.oauth_login_requested.connect(self.get_license_with_oauth)

        self.license_manager.license_applied.connect(self._handle_license_applied)
        self.license_manager.error.connect(self._handle_error)

    def _init_products(self):
        def on_success(license_info: LicenseInfo):
            product = LicensedProduct(
                name=self.BRAINFRAME_PRODUCT_NAME,
                icon_resource=self.BRAINFRAME_PRODUCT_ICON,
                license_info=license_info,
            )
            self.product_sidebar.add_product(product)

            # BrainFrame product should always be first in list
            self.product_sidebar.setCurrentRow(0)

        def on_error(exc: BaseException):
            if isinstance(exc, bf_errors.ServerNotReadyError):
                self._handle_connection_error(exc)
            else:
                self._handle_unknown_error(exc)

        QTAsyncWorker(self, licensing.get_brainframe_license_info,
                      on_success=on_success, on_error=on_error) \
            .start()

    def change_product(self, item: QListWidgetItem, _previous: QListWidgetItem) -> None:
        widget: ProductWidget = self.product_sidebar.itemWidget(item)

        self.license_details.set_product(widget.product)

    def get_license_with_oauth(self) -> None:
        working_indicator = WorkingIndicator(parent=self)
        working_indicator.setLabelText(self.tr("Authenticating with OAuth..."))
        working_indicator.show()

        self.license_manager.license_applied.connect(
            lambda _: working_indicator.cancel())

        self.license_manager.error.connect(lambda _: working_indicator.cancel())

        # TODO: This creates a loop
        # working_indicator.canceled.connect(self.license_manager.cancel_oauth)

        self.license_manager.authenticate_with_oauth()

    def send_update_license_text(self, license_key: str):
        working_indicator = WorkingIndicator(parent=self)
        working_indicator.setLabelText(self.tr("Uploading license..."))
        working_indicator.show()

        self.license_manager.license_applied.connect(
            lambda _: working_indicator.cancel())
        self.license_manager.error.connect(lambda _: working_indicator.cancel())

        # TODO:
        # working_indicator.canceled.connect(self.license_manager.cancel_oauth)

        # TODO: Remove any Cloud User information from client

        self.license_manager.authenticate_with_license_key(license_key)

    def update_license_info(self, product: LicensedProduct) -> None:
        self.product_sidebar.update_product(product)

        # Only change the license details if the product is already displayed
        if self.license_details.product_name == product.name:
            self.license_details.set_product(product)

    def _handle_license_applied(self, license_info: LicenseInfo) -> None:
        product = LicensedProduct(
            name=self.BRAINFRAME_PRODUCT_NAME,
            icon_resource=self.BRAINFRAME_PRODUCT_ICON,
            license_info=license_info,
        )
        self.update_license_info(product)

        BrainFrameMessage.information(
            parent=self,
            title=self.tr("License applied"),
            message=self.tr("License successfully applied to server")
        ).exec()

    def _handle_error(self, exc) -> None:
        if isinstance(exc, bf_errors.LicenseInvalidError):
            self._handle_invalid_license_error(exc)
        elif isinstance(exc, bf_errors.LicenseExpiredError):
            self._handle_expired_license_error(exc)
        elif isinstance(exc, bf_errors.RemoteConnectionError):
            self._handle_license_server_connection_error(exc)
        elif isinstance(exc, bf_errors.UnauthorizedTokensError):
            self._handle_unauthorized_tokens_error(exc)
        else:
            raise exc

    def _handle_invalid_license_error(self, _exc):

        message_title = self.tr("Invalid License Format")
        # TODO: BF-1332 - Failed online check-in results in an Invalid license
        message = self.tr(
            "The provided license has an invalid format. Please "
            "<a href='{license_docs_link}'>upload a new license</a>.") \
            .format(license_docs_link=LICENSE_DOCS_LINK)

        BrainFrameMessage.information(
            parent=self,
            title=message_title,
            message=message
        ).exec()

    def _handle_expired_license_error(self, _exc):

        message_title = self.tr("Expired License")
        message = self.tr(
            "The provided license has expired. Please "
            "<a href='{license_docs_link}'>upload a new license</a>.") \
            .format(license_docs_link=LICENSE_DOCS_LINK)

        BrainFrameMessage.information(
            parent=self,
            title=message_title,
            message=message
        ).exec()

    def _handle_license_server_connection_error(self, _exc):
        message_title = self.tr("License Server Connection Failure")
        message = self.tr(
            "The BrainFrame server was unable to contact the licensing server "
            "to validate the license. Please ensure that the BrainFrame "
            "server has internet access.")

        BrainFrameMessage.information(
            parent=self,
            title=message_title,
            message=message
        ).exec()

    def _handle_unauthorized_tokens_error(self, _exc):
        message_title = self.tr("Unauthorized Tokens")
        message = self.tr(
            "The BrainFrame server was unable to authenticate with the licensing "
            "server to retrieve a license. Please ensure that the tokens have not "
            "expired and are for the proper licensing server."
        )

        BrainFrameMessage.information(
            parent=self,
            title=message_title,
            message=message
        ).exec()
