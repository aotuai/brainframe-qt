import logging

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QHostAddress
from PyQt5.QtNetworkAuth import QOAuthHttpServerReplyHandler

from brainframe_qt.util.oauth.base import AuthTokenResponse


class PKCEReplyHandler(QOAuthHttpServerReplyHandler):
    ready = pyqtSignal()
    """Emitted when the ReplyHandler is ready for connections"""
    completed = pyqtSignal(AuthTokenResponse)
    """Emitted when the ReplyHandler has received an Authorization Code"""

    _PORTS = [21849, 32047, 31415]

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self.close()  # Constructor starts at a useless address/port

        self._init_signals()

    def _init_signals(self) -> None:
        self.callbackReceived.connect(self._on_callback_received)

    def start(self) -> None:
        """Start listening"""
        for port in self._PORTS:
            logging.debug(f"PKCEReplyHandler attempting to listen at localhost:{port}")
            if self.listen(address=QHostAddress.LocalHost, port=port):
                break

        else:
            logging.error("Unable to start PKCEReplyHandler on any configured port")
            return

        logging.debug(f"PKCEReplyHandler listening at localhost:{port}")
        self.ready.emit()

    def _on_callback_received(self, values: dict) -> None:
        logging.debug(f"Callback received data: {values}")

        if "code" not in values:
            # Unknown connection/data
            return

        if "state" not in values:
            # Unknown connection/data
            return

        auth_response = AuthTokenResponse(
            authorization_code=values["code"],
            state=values["state"]
        )

        self.completed.emit(auth_response)
