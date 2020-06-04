import datetime

import pendulum
from PyQt5.QtWidgets import QWidget

from brainframe.api import bf_codecs
from brainframe.client.api_utils import api
from brainframe.client.ui.resources import QTAsyncWorker
from .license_dialog_ui import _LicenseDialogUI


class LicenseDialog(_LicenseDialogUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

        self._init_products()

    def _init_signals(self) -> None:
        ...

    def _init_products(self):
        def on_success(license_info: bf_codecs.LicenseInfo):
            _exp_date = license_info.terms.expiration_date
            expiration = self._date_to_pdl_datetime(_exp_date)

            icon_path = ":/icons/capsule_toolbar"
            self.product_sidebar.add_product(
                "BrainFrame", expiration, icon_path)

        def on_error():
            pass

        QTAsyncWorker(self, api.get_license_info,
                      on_success=on_success, on_error=on_error) \
            .start()

        # TODO: Also get capsule information if that's ever added

    @staticmethod
    def _date_to_pdl_datetime(date: datetime.date) -> pendulum.DateTime:
        pdl_datetime = pendulum.datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            tz="UTC")

        return pdl_datetime
