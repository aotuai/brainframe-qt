from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QDesktopServices

from brainframe.api import bf_codecs, bf_errors

from brainframe_qt import constants
from brainframe_qt.api_utils import api
from brainframe_qt.ui.resources import QTAsyncWorker
from brainframe_qt.util.licensing import LicenseInfo
from brainframe_qt.util.oauth.error import OAuthError


class LicenseManager(QObject):
    sign_in_successful = pyqtSignal(bf_codecs.CloudUserInfo)
    license_applied = pyqtSignal(LicenseInfo)

    api_error = pyqtSignal(bf_errors.BaseAPIError)
    oauth_error = pyqtSignal(OAuthError)

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        if self.is_oauth_available():
            from brainframe_qt.util.oauth.cognito import CognitoOAuth
            self.oauth = CognitoOAuth(
                cognito_domain=constants.oauth.COGNITO_DOMAIN,
                client_id=constants.oauth.CLIENT_ID,
                parent=self,
            )
        else:
            self.oauth = None

        self._init_signals()

    def _init_signals(self) -> None:
        if self.is_oauth_available():
            self.oauth.ready_to_authenticate.connect(QDesktopServices.openUrl)
            self.oauth.authentication_successful.connect(self.authenticate_with_tokens)
            self.oauth.authentication_error.connect(self.oauth_error)

    def authenticate_with_oauth(self):
        if not self.is_oauth_available():
            raise RuntimeError("OAuth is not available on this platform.")
        self.oauth.authenticate()

    def authenticate_with_tokens(self, tokens: bf_codecs.CloudTokens) -> None:
        def on_success(token_response) -> None:
            cloud_user_info: bf_codecs.CloudUserInfo
            api_license_info: bf_codecs.LicenseInfo
            cloud_user_info, api_license_info = token_response

            license_info = LicenseInfo.from_api_info(api_license_info)

            self.sign_in_successful.emit(cloud_user_info)
            self.license_applied.emit(license_info)

        QTAsyncWorker(self, api.set_cloud_tokens, f_args=(tokens,),
                      on_success=on_success, on_error=self.api_error.emit) \
            .start()

    def authenticate_with_license_key(self, license_key: str) -> None:
        def on_success(api_license_info: bf_codecs.LicenseInfo) -> None:
            license_info = LicenseInfo.from_api_info(api_license_info)

            self.license_applied.emit(license_info)

        QTAsyncWorker(self, api.set_license_key, f_args=(license_key,),
                      on_success=on_success, on_error=self.api_error.emit) \
            .start()

    @staticmethod
    def is_oauth_available() -> bool:
        # We've been unable to get QtNetworkAuth installed for Windows within MSYS
        try:
            from PyQt5 import QtNetworkAuth
        except ImportError:
            return False
        else:
            return True
