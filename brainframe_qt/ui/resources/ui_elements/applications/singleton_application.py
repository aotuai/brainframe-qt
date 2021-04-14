import logging
import sys
import tempfile
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import pyqtSignal, QLockFile, Qt
from PyQt5.QtWidgets import QWidget

from .messaging_application import MessagingApplication


class SingletonApplication(MessagingApplication):
    """A QApplication that expects to be the only instance running. Uses a
    lockfile to ascertain as such.

    If another instance is running, sends a new_instance_attempted message to it
    and then closes
    """
    new_instance_attempted = pyqtSignal()

    def __init__(self, *, internal_name: str):

        # Try to acquire global lock first
        self._lock: Optional[InstanceLock]
        try:
            self._lock = InstanceLock(internal_name)
        except InstanceLock.DuplicateInstanceError:
            self._lock = None

        super().__init__(socket_name=internal_name, force_client=self._lock is None)

        self._main_window: Optional[QWidget] = None

        self.internal_name = internal_name

        self._new_instance_attempted_msg = self.register_new_message(
            message_str="new_instance_attempted",
            signal=self.new_instance_attempted
        )
        self.new_instance_attempted.connect(self._bring_main_window_to_front)

        # We weren't able to acquire a lock before, so we need to close
        if self._lock is None:
            self._close_as_duplicate_instance()

    @property
    def main_window(self) -> QWidget:
        return self._main_window

    @main_window.setter
    def main_window(self, widget: QWidget) -> None:
        self._main_window = widget

    def _close_as_duplicate_instance(self) -> None:
        logging.warning("Client is already running. Using other instance "
                        "instead.")

        self.message_socket.send_message(self._new_instance_attempted_msg)

        # Can't use QApplication.quit() because EventLoop hasn't started
        sys.exit()

    def _bring_main_window_to_front(self) -> None:
        current_state = self.main_window.windowState()
        self.main_window.setWindowState(current_state & ~Qt.WindowMinimized)
        self.main_window.raise_()
        self.main_window.activateWindow()


class InstanceLock(QLockFile):
    """Lock file that raises a DuplicateInstanceError if already locked by
    another instance"""
    _TRY_LOCK_TIMEOUT = 50  # milliseconds

    class DuplicateInstanceError(RuntimeError):
        ...

    def __init__(self, lock_name: str):
        self._lock_name = lock_name

        super().__init__(str(self.filepath))

        # As we hold lock indefinitely, never let it become stale
        self.setStaleLockTime(0)

        if not self.tryLock(timeout=self._TRY_LOCK_TIMEOUT):
            raise self.DuplicateInstanceError()

    @property
    def filepath(self) -> Path:
        return Path(tempfile.gettempdir(), f"{self._lock_name}.lock")

    def __del__(self):
        """Deletes the lockfile if owned, otherwise does nothing"""
        self.unlock()
