import base64
import hashlib
import json
import secrets
import string
import uuid
from json import JSONDecodeError
from typing import Tuple

from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QUrlQuery
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply

from brainframe.api import bf_codecs

from brainframe_qt import constants
from brainframe_qt.util.oauth.base import AuthTokenResponse
from brainframe_qt.util.oauth.error import OAuthError
from brainframe_qt.util.oauth.reply_handler import PKCEReplyHandler


class CognitoOAuth(QObject):
    """Performs OAuth2 Authorization Code Flow with PKCE with Aotu's Cognito instance"""

    ready_to_authenticate = pyqtSignal(QUrl)
    """Emitted when the Authentication URL is ready to be opened in a browser window
    on the client computer for authentication"""

    authentication_successful = pyqtSignal(bf_codecs.CloudTokens)
    """Emitted when Authentication is successful and both Access and Refresh Tokens have
    been acquired"""

    authentication_error = pyqtSignal(OAuthError)
    """Emitted when there was an Error during the Authentication procedure"""

    class InvalidStateError(OAuthError):
        """State returned to redirect_uri did not match state sent to auth server"""

    class InvalidTokenResponse(OAuthError):
        """Reply to Access and Refresh Tokens request was invalid"""

    class ReplyHandlerError(OAuthError):
        """An error occurred in the PKCEReplyHandler"""

    _SCOPES = ["email", "aws.cognito.signin.user.admin", "profile", "openid",
               *constants.oauth.OAUTH_SCOPES]

    def __init__(self, *, cognito_domain: str, client_id: str, parent: QObject):
        super().__init__(parent=parent)

        self.cognito_domain = cognito_domain
        """Cognito hosted sign-in core"""
        self.client_id = client_id
        """Client ID of the Application known by the Authentication server"""

        self._code_challenge, self._code_verifier = self._make_pkce_code()
        self._state = self._make_state()

        self._reply_handler = self._init_reply_handler()

        self._init_signals()

    def _init_reply_handler(self) -> "PKCEReplyHandler":
        reply_handler = PKCEReplyHandler(parent=self)
        return reply_handler

    def _init_signals(self) -> None:
        self._reply_handler.ready.connect(self._on_reply_handler_ready)
        self._reply_handler.completed.connect(self._on_reply_handler_completed)
        self._reply_handler.error.connect(self._on_reply_handler_error)

    def authenticate(self) -> None:
        """Start the Authentication procedure"""
        self._reply_handler.start()

    @property
    def authorization_url(self) -> QUrl:
        """URL to request the user's Authorization Token and redirect back to the
        application"""
        url = QUrl(f"https://{self.cognito_domain}/oauth2/authorize")

        scope = " ".join(self._SCOPES)

        query = QUrlQuery()
        query.addQueryItem("response_type", "code")
        query.addQueryItem("client_id", self.client_id)
        query.addQueryItem("scope", scope)
        query.addQueryItem("redirect_uri", self.callback_url.toString())
        query.addQueryItem("state", self._state)
        query.addQueryItem("identity_provider", "COGNITO")
        query.addQueryItem("code_challenge_method", "S256")
        query.addQueryItem("code_challenge", self._code_challenge)
        url.setQuery(query)

        return url

    @property
    def callback_url(self) -> QUrl:
        """Redirect URL to supply to the authorization and token requests"""
        # Qt insists on using loopback for callback URI, but Cognito only allows
        # localhost
        callback_url = self._reply_handler.callback().replace("127.0.0.1", "localhost")
        return QUrl(callback_url)

    @property
    def token_url(self) -> QUrl:
        """URL to request the user's Access and Refresh Tokens"""
        return QUrl(f"https://{self.cognito_domain}/oauth2/token")

    def _on_reply_handler_completed(self, auth_response: AuthTokenResponse) -> None:
        """Called when the ReplyHandler has received an Authorization token"""
        if auth_response.state != self._state:
            self.authentication_error.emit(self.InvalidStateError())
            return

        network_manager = QNetworkAccessManager(parent=self)
        network_manager.finished.connect(self._on_token_reply)

        # Surely there's a better way to do this
        callback_url = QUrl.toPercentEncoding(self.callback_url.toString())
        callback_url = bytes(callback_url).decode()

        body = (
            f"grant_type=authorization_code"
            f"&client_id={self.client_id}"
            f"&code_verifier={self._code_verifier}"
            f"&code={auth_response.authorization_code}"
            f"&redirect_uri={callback_url}"
        )
        request = QNetworkRequest(self.token_url)
        request.setHeader(
            request.ContentTypeHeader, "application/x-www-form-urlencoded"
        )

        network_manager.post(request, body.encode())

    def _on_reply_handler_error(self, error: OAuthError) -> None:
        new_error = self.ReplyHandlerError()
        new_error.__cause__ = error
        self.authentication_error.emit(new_error)

    def _on_reply_handler_ready(self) -> None:
        self.ready_to_authenticate.emit(self.authorization_url)

    def _on_token_reply(self, reply: QNetworkReply) -> None:
        """Called when the Access and Refresh Token completes"""
        try:
            response = json.loads(bytes(reply.readAll()))
        except JSONDecodeError as exc:
            exception = self.InvalidTokenResponse()
            exception.__cause__ = exc

            self.authentication_error.emit(exception)
            return

        try:
            access_token = response["access_token"]
            refresh_token = response["refresh_token"]
        except KeyError as exc:
            exception = self.InvalidTokenResponse()
            exception.__cause__ = exc

            self.authentication_error.emit(exception)
            return

        tokens = bf_codecs.CloudTokens(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        self.authentication_successful.emit(tokens)

    @staticmethod
    def _make_pkce_code() -> Tuple[str, str]:
        """Generates a PKCE code and returns a code challenge and code verifier. The
        code challenge is provided to Cognito when the flow starts, and the code
        verifier is provided when requesting the access and refresh tokens. These values
        are used by Cognito to ensure that it's talking to the same client throughout
        the entire flow.
        """
        alphanumeric = string.ascii_letters + string.digits
        code_verifier = "".join(secrets.choice(alphanumeric) for _ in range(128))

        code_challenge = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = (base64.urlsafe_b64encode(code_challenge)
                          .decode()
                          .replace("=", ""))

        return code_challenge, code_verifier

    @staticmethod
    def _make_state() -> str:
        return str(uuid.uuid4())


if __name__ == '__main__':
    import typing

    from PyQt5.QtGui import QDesktopServices
    from PyQt5.QtWidgets import QApplication, QWidget

    app = QApplication([])

    oauth = CognitoOAuth(
        cognito_domain=constants.oauth.COGNITO_DOMAIN,
        client_id=constants.oauth.CLIENT_ID,
        parent=typing.cast(QWidget, None),
    )

    def on_success(tokens: bf_codecs.CloudTokens) -> None:
        print(tokens)
        app.exit()

    oauth.ready_to_authenticate.connect(QDesktopServices.openUrl)
    oauth.authentication_successful.connect(on_success)

    oauth.authenticate()

    app.exec()
