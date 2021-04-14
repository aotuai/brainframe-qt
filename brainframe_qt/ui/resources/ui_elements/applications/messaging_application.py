import logging
import typing
from typing import NewType, Dict, Optional

from PyQt5 import sip
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

    def _init_message_server(self, socket_name: str, retries: int = 0) \
            -> Optional["MessagingServer"]:

        # Check if there's already an active server that is ready to communicate
        if MessagingSocket.is_server_alive(socket_name):
            return None

        # Otherwise, try becoming the server
        message_server = MessagingServer(socket_name=socket_name, parent=self)

        # Note that this will only trigger on Linux:
        # https://doc.qt.io/qt-5/qlocalserver.html#listen
        # """
        #   Note: On Unix if the server crashes without closing listen will fail with
        #   AddressInUseError. To create a new server the file should be removed. On
        #   Windows two local servers can listen to the same pipe at the same time, but
        #   any connections will go to one of the server.
        # """
        if message_server.serverError() == QAbstractSocket.AddressInUseError:
            if retries > 3:
                # Already retried. Give up trying to create the server.
                logging.error(f"Max retries reached. Giving up on socket takeover")
                return None

            logging.warning(f"Socket for IPC is open, but connection was refused. "
                            f"Attempting takeover.")
            # Attempt hostile takeover of socket
            MessagingServer.removeServer(socket_name)
            message_server = self._init_message_server(socket_name, retries=retries + 1)

            if message_server:
                logging.info("IPC server socket takeover successful")
            else:
                logging.error("Unable to perform takeover on socket")

        return message_server

    def _init_message_socket(self, server_name: str) -> "MessagingSocket":
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
        self.previous_connection: Optional[QLocalSocket] = None

        self.newConnection.connect(self._handle_connection)

        self.listen(socket_name)

    def _get_socket(self) -> Optional[QLocalSocket]:
        # Modeled after
        # https://github.com/qutebrowser/qutebrowser/blob/dacaefaf/qutebrowser/misc/ipc.py#L359-L381
        if self.current_connection is not None:
            socket = self.current_connection
        elif self.previous_connection is not None:
            logging.debug(
                "Attempted to get current socket, but current socket was None. Using "
                "previous socket"
            )
            socket = self.previous_connection
        else:
            logging.warning(
                "Attempted to retrieve current socket, but there is no current socket"
            )
            return None

        if sip.isdeleted(socket):
            logging.error("Attempted to retrieve deleted socket")
            return None

        return socket

    def _handle_connection(self) -> None:
        """Called when a new connection is made to the server.

        Connects handler functions to the different events that can occur with a socket
        """
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
            logging.debug("immediate _handle_ready_read")
            self._handle_ready_read()
        else:
            logging.debug("connect _handle_ready_read")
            socket.readyRead.connect(self._handle_ready_read)

        if socket.error() not in [
            socket.UnknownSocketError, socket.PeerClosedError
        ]:
            # Immediate error
            logging.debug("immediate _handle_socket_error")
            self._handle_socket_error(socket.error())
        else:
            logging.debug("connect _handle_socket_error")
            socket.error.connect(self._handle_socket_error)

        if socket.state() == QLocalSocket.UnconnectedState:
            # Immediate disconnect
            logging.debug("immediate _handle_disconnect")
            self._handle_disconnect()
        else:
            logging.debug("connect _handle_disconnect")
            socket.disconnected.connect(self._handle_disconnect)

    def _handle_disconnect(self) -> None:
        logging.debug("exec _handle_disconnect")

        if self.previous_connection is not None:
            self.previous_connection.deleteLater()

        socket = self.current_connection
        logging.debug(f"Client disconnected from server: 0x{id(socket):x}")

        self.previous_connection, self.current_connection = (
            self.current_connection, None
        )

        # Deal with potential queue of connections
        self._handle_connection()

    def _handle_ready_read(self) -> None:
        logging.debug("exec _handle_ready_read")

        socket = self._get_socket()
        if socket is None:
            logging.error(
                "Attempted to read message from socket, but socket has already been "
                "disconnected/deleted"
            )
            return

        message_data = bytes(socket.readAll())
        logging.debug(f"Received raw data from socket 0x{id(socket):x}: {message_data}")

        message = self._parse_message_data(message_data)
        self.new_message.emit(message)

    def _handle_socket_error(self, error: QLocalSocket.LocalSocketError) -> None:
        logging.debug(f"exec _handle_socket_error | {error}")
        socket = self._get_socket()

        if socket is None:
            logging.error(
                "Attempted to deal with socket error, but socket has already been "
                "disconnected/deleted"
            )
            return

        if socket.error() == socket.PeerClosedError:
            logging.debug(f"Peer disconnected on socket 0x{id(socket):x}")
        else:
            error_message = (
                f"Error occurred with IPC socket 0x{id(socket):x}: "
                f"{error} | {self.errorString()}"
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

    class UnknownConnectionError(RuntimeError):
        def __init__(self, server_name: str, error: QLocalSocket.LocalSocketError,
                     error_string: str):
            super().__init__(
                f"Unknown error while attempting to connect to Messaging Server at "
                f'"{server_name}": '
                f"QLocalSocket.LocalSocketError={error} | {error_string}"
            )

    _CONNECTION_TIMEOUT = 5000  # milliseconds
    _MESSAGE_SEND_TIMEOUT = 5000  # milliseconds

    def __init__(self, *, server_name: str, parent: QObject):
        super().__init__(parent)

        self.setServerName(server_name)

    def send_message(self, message: IntraInstanceMessage) -> None:
        """Send a message to the server Application. *Blocking call.*"""

        # If an error occurs while connecting to the server, this property is set to
        # None. Cache it to use it for error messages.
        server_name = self.serverName()

        logging.debug(f"Sending message to main instance: {message}")
        self.connectToServer(QLocalSocket.WriteOnly)

        # After QLocalSocket.connectToServer is called, the socket state will be one of
        # the following unless an error has occurred
        if self.state() not in [
            QLocalSocket.ConnectingState,
            QLocalSocket.ConnectedState
        ]:
            raise self.UnknownConnectionError(
                server_name=server_name,
                error=self.error(),
                error_string=self.errorString()
            )

        # Wait for connection to establish if it didn't happen immediately
        if not self.waitForConnected(self._CONNECTION_TIMEOUT):
            raise self.ConnectionTimeoutError()

        # Write our message
        self.write(message.encode())

        # Wait for message to be completely written. I guess QLocalSocket.write can
        # finish early?
        if not self.waitForBytesWritten(self._MESSAGE_SEND_TIMEOUT):
            raise self.MessageSendTimeoutError()

        logging.debug(f"Message sending complete")

        # Disconnect from server and wait for disconnect to finish
        self.disconnectFromServer()
        if self.state() != QLocalSocket.UnconnectedState:
            self.waitForDisconnected(self._CONNECTION_TIMEOUT)

    @classmethod
    def is_server_alive(cls, server_name) -> bool:
        """Check if the server Application is still accepting connections on its
         socket"""

        tmp_socket = cls(
            server_name=server_name,
            parent=typing.cast(QObject, None)
        )

        tmp_socket.connectToServer(QLocalSocket.ReadOnly)

        connection_successful = tmp_socket.waitForConnected(cls._CONNECTION_TIMEOUT)

        tmp_socket.disconnectFromServer()

        return connection_successful
