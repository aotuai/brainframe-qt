from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QDesktopServices
from brainframe.api.bf_codecs import CloudUserInfo, LicenseInfo, CloudTokens
from brainframe.api.bf_errors import BaseAPIError

from brainframe_qt import constants
from brainframe_qt.api_utils import api
from brainframe_qt.ui.resources import QTAsyncWorker
from brainframe_qt.util.oauth.cognito import CognitoOAuth


class LicenseManager(QObject):
    sign_in_successful = pyqtSignal(CloudUserInfo)
    license_applied = pyqtSignal(LicenseInfo)
    error = pyqtSignal(BaseAPIError)

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self.oauth = CognitoOAuth(
            cognito_domain=constants.oauth.COGNITO_DOMAIN,
            client_id=constants.oauth.CLIENT_ID,
            parent=self,
        )

        self._init_signals()

    def _init_signals(self) -> None:
        self.oauth.ready_to_authenticate.connect(QDesktopServices.openUrl)
        self.oauth.authentication_successful.connect(self.authenticate_with_tokens)
        self.oauth.authentication_error.connect(self.error)

    def authenticate_with_oauth(self):
        self.oauth.authenticate()

    def authenticate_with_tokens(self, tokens: CloudTokens) -> None:
        def on_success(token_response) -> None:
            cloud_user_info: CloudUserInfo
            license_info: LicenseInfo
            cloud_user_info, license_info = token_response

            self.sign_in_successful.emit(cloud_user_info)
            self.license_applied.emit(license_info)

        QTAsyncWorker(self, api.set_cloud_tokens, f_args=(tokens,),
                      on_success=on_success, on_error=self.error.emit) \
            .start()

    def authenticate_with_license_key(self, license_key: str) -> None:
        QTAsyncWorker(self, api.set_license_key, f_args=(license_key,),
                      on_success=self.license_applied.emit, on_error=self.error.emit) \
            .start()

    def cancel_oauth(self) -> None:
        self.oauth.cancel_authentication()


"""
brainframe.api.bf_errors.UnknownError: UnknownError: 404 Not Found


Traceback (most recent call last):
  File "/home/ignormies/doc/git/aotu/brainframe-qt/brainframe_qt/ui/dialogs/license_dialog/license_dialog.py", line 127, in _handle_error
    self._handle_unknown_error(exc)
  File "/home/ignormies/doc/git/aotu/brainframe-qt/brainframe_qt/ui/dialogs/license_dialog/license_dialog.py", line 186, in _handle_unknown_error
    raise exc
  File "/home/ignormies/doc/git/aotu/brainframe-qt/brainframe_qt/ui/resources/qt_async_worker.py", line 47, in run
    self.data = self.func(*self.f_args, **self.f_kwargs)
  File "/home/ignormies/.cache/pypoetry/virtualenvs/brainframe-D8O-9Dia-py3.9/lib/python3.9/site-packages/brainframe/api/stubs/cloud_tokens.py", line 17, in set_cloud_tokens
    login_result = self._put_codec(req, timeout, cloud_tokens)
  File "/home/ignormies/.cache/pypoetry/virtualenvs/brainframe-D8O-9Dia-py3.9/lib/python3.9/site-packages/brainframe/api/stubs/base_stub.py", line 70, in _put_codec
    resp = self._put(api_url,
  File "/home/ignormies/.cache/pypoetry/virtualenvs/brainframe-D8O-9Dia-py3.9/lib/python3.9/site-packages/brainframe/api/stubs/base_stub.py", line 201, in _put
    return self._send_authorized(request, timeout)
  File "/home/ignormies/.cache/pypoetry/virtualenvs/brainframe-D8O-9Dia-py3.9/lib/python3.9/site-packages/brainframe/api/stubs/base_stub.py", line 300, in _send_authorized
    resp = send_func(request, timeout)
  File "/home/ignormies/.cache/pypoetry/virtualenvs/brainframe-D8O-9Dia-py3.9/lib/python3.9/site-packages/brainframe/api/stubs/base_stub.py", line 314, in _send_with_credentials
    resp = self._perform_request(request, timeout)
  File "/home/ignormies/.cache/pypoetry/virtualenvs/brainframe-D8O-9Dia-py3.9/lib/python3.9/site-packages/brainframe/api/stubs/base_stub.py", line 347, in _perform_request
    raise _make_api_error(resp=resp)
brainframe.api.bf_errors.UnknownError: UnknownError: 404 Not Found
"""
