from __future__ import annotations

import logging
import typing
from typing import NewType, Dict, Optional

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtNetwork import QLocalServer, QLocalSocket, QAbstractSocket
from PyQt5.QtWidgets import QApplication

IntraInstanceMessage = NewType("IntraInstanceMessage", str)


class MessagingApplication(QApplication):
    """A QApplication that supports IPC over sockets"""

    class UnknownMessageError(RuntimeError):
        ...

    def __init__(self, *, socket_name: str):
        super().__init__([])

        self._known_messages: Dict[IntraInstanceMessage, pyqtSignal] = {}

        # Application will either be a server or client (with socket)
        self.message_server = self._init_message_server(socket_name)
        self.message_socket = (
            self._init_message_socket(socket_name)
            if not self.message_server
            else None
        )

        self._init_signals()

    def _init_message_server(self, socket_name: str) \
            -> Optional[MessagingServer]:
        message_server = MessagingServer(socket_name=socket_name, parent=self)

        if message_server.serverError() == QAbstractSocket.AddressInUseError:
            if not MessagingSocket.is_server_alive(socket_name):
                logging.warning(f"Socket for IPC is open, but connection was "
                                "refused. Attempting takeover.")
                # Attempt hostile takeover of socket
                MessagingServer.removeServer(socket_name)
                message_server = self._init_message_server(socket_name)

                if message_server:
                    logging.info("IPC server socket takeover successful.")
                else:
                    logging.error("Unable to perform takeover on socket.")
            else:
                return None

        return message_server

    def _init_message_socket(self, server_name: str) -> MessagingSocket:
        message_socket = MessagingSocket(server_name=server_name, parent=self)

        return message_socket

    def _init_signals(self) -> None:
        if self.is_server:
            self.message_server.new_message.connect(self._handle_message)

    @property
    def is_server(self) -> bool:
        """Whether the current Application is the server"""
        return self.message_server is not None

    @property
    def is_client(self) -> bool:
        """Whether the current Application is a client to another server"""
        return self.message_socket is not None

    def register_new_message(
            self, message_str: str, signal: pyqtSignal
    ) -> IntraInstanceMessage:
        """Register a signal to be called when a message is received"""
        message = IntraInstanceMessage(message_str)
        self._known_messages[message] = signal

        return message

    def _get_message_signal(self, message: IntraInstanceMessage) -> pyqtSignal:
        """Retrieve the signal associated with a message"""
        message_signal = self._known_messages.get(message)
        if message_signal is not None:
            return message_signal
        else:
            raise self.UnknownMessageError(f"Unknown message {message}")

    def _handle_message(self, message: IntraInstanceMessage) -> None:
        try:
            message_signal = self._get_message_signal(message)
        except self.UnknownMessageError:
            logging.warning(f"Received unknown IPC message: {message}")
            return

        message_signal.emit()


class MessagingServer(QLocalServer):
    """Server used to receive messages from other instances

    Emits new_message signal with message when a message is received.
    """

    class MessageReadTimeoutError(TimeoutError):
        ...

    class UnknownSocketError(RuntimeError):
        ...

    new_message = pyqtSignal(str)

    def __init__(self, *, socket_name: str, parent: QObject):
        super().__init__(parent)

        self.current_connection: Optional[QLocalSocket] = None
        self.newConnection.connect(self._handle_connection)

        self.listen(socket_name)

    def _handle_connection(self) -> None:
        if not self.hasPendingConnections():
            # Probably called from the end of _handle_disconnect()
            return

        if self.current_connection is not None:
            logging.debug(
                f"Received new connection, but we're already handling another: "
                f"0x{id(self.current_connection):x}"
            )

        self.current_connection = socket = self.nextPendingConnection()
        logging.debug(f"Client connected to server: 0x{id(socket):x}")

        if socket.canReadLine():
            # Immediate ready to read data
            self._handle_ready_read()
        else:
            socket.readyRead.connect(self._handle_ready_read)

        if socket.error() not in [
            socket.UnknownSocketError, socket.PeerClosedError
        ]:
            # Immediate error
            self._handle_socket_error()
        else:
            socket.error.connect(self._handle_socket_error)

        if socket.state() == QLocalSocket.UnconnectedState:
            # Immediate disconnect
            self._handle_disconnect()
        else:
            socket.disconnected.connect(self._handle_disconnect)

    def _handle_disconnect(self) -> None:
        socket = self.current_connection
        logging.debug(f"Client disconnected from server: 0x{id(socket):x}")

        self.current_connection = None

        # Deal with potential queue of connections
        self._handle_connection()

    def _handle_ready_read(self) -> None:
        socket = self.current_connection
        message_data = bytes(socket.readAll())
        logging.debug(
            f"Received raw data from socket 0x{id(socket):x}: "
            f"{message_data}"
        )
        message = self._parse_message_data(message_data)
        self.new_message.emit(message)

    def _handle_socket_error(self, _error: QLocalSocket.LocalSocketError) \
            -> None:
        socket = self.current_connection

        if socket.error() == socket.PeerClosedError:
            logging.debug(f"Peer disconnected on socket 0x{id(socket):x}")
        else:
            error_message = (
                f"Error occurred with IPC socket 0x{id(socket):x}: "
                f"{socket.error()} | {self.errorString()}"
            )
            logging.error(error_message)
            raise self.UnknownSocketError(error_message)

    # noinspection PyMethodMayBeStatic
    def _parse_message_data(self, message_data: bytes) -> IntraInstanceMessage:
        # TODO: Support extra args?
        # TODO: Handle decoding errors
        message = IntraInstanceMessage(message_data.decode())

        logging.debug(f"Received message from client: {message}")

        return message


class MessagingSocket(QLocalSocket):
    class ConnectionTimeoutError(TimeoutError):
        ...

    class MessageSendTimeoutError(TimeoutError):
        ...

    _CONNECTION_TIMEOUT = 5000  # milliseconds
    _MESSAGE_SEND_TIMEOUT = 5000  # milliseconds

    def __init__(self, *, server_name: str, parent: QObject):
        super().__init__(parent)

        self.setServerName(server_name)

    def send_message(self, message: IntraInstanceMessage) -> None:
        """Send a message to the server Application. *Blocking call.*"""

        logging.debug(f"Sending message to main instance: {message}")
        self.connectToServer(QLocalSocket.WriteOnly)

        if not self.waitForConnected(self._CONNECTION_TIMEOUT):
            raise self.ConnectionTimeoutError()

        self.write(message.encode())

        if not self.waitForBytesWritten(self._MESSAGE_SEND_TIMEOUT):
            raise self.MessageSendTimeoutError()

        logging.debug(f"Message sending complete")

        self.disconnectFromServer()

    @classmethod
    def is_server_alive(cls, server_name) -> bool:
        """Check if the server Application is still accepting connections on its
         socket"""

        tmp_socket = cls(
            server_name=server_name,
            parent=typing.cast(QObject, None)
        )
        tmp_socket.connectToServer(MessagingSocket.ReadOnly)

        # TODO: Should we check for _any_ error (i.e. != -1)?
        connection_was_refused = (
                tmp_socket.error() == MessagingSocket.ConnectionRefusedError
        )

        tmp_socket.disconnectFromServer()

        return not connection_was_refused
