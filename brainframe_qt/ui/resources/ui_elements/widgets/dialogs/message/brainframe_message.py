import typing
from enum import Flag, auto
from traceback import TracebackException
from typing import Callable, Optional

from PyQt5.QtWidgets import QAbstractButton, QApplication, QMessageBox, \
    QPushButton, QWidget

from brainframe_qt.ui.resources import actions
from .brainframe_message_ui import _BrainFrameMessageUI


class BrainFrameMessage(_BrainFrameMessageUI):
    class PresetButtons(Flag):
        NONE = 0

        OK = auto()
        YES = auto()
        NO = auto()
        CLOSE_CLIENT = auto()
        COPY_TO_CLIPBOARD = auto()
        SERVER_CONFIG = auto()

        INFORMATION = OK
        QUESTION = YES | NO
        WARNING = OK | COPY_TO_CLIPBOARD
        EXCEPTION = CLOSE_CLIENT | COPY_TO_CLIPBOARD | SERVER_CONFIG
        ERROR = CLOSE_CLIENT | COPY_TO_CLIPBOARD | SERVER_CONFIG
        CRITICAL = CLOSE_CLIENT | COPY_TO_CLIPBOARD

    def __init__(self, *, parent: QWidget, title: str, text: str,
                 subtext: Optional[str], buttons: PresetButtons):
        super().__init__(parent)

        self._title: str = typing.cast(str, None)
        self._text: str = typing.cast(str, None)

        self._traceback: Optional[TracebackException] = None

        self.title = title
        self.text = text
        self.subtext = subtext
        self._create_preset_buttons(buttons)

    # noinspection PyMethodOverriding
    @classmethod
    def information(cls, *, parent: QWidget, title: str, message: str,
                    subtext: Optional[str] = None,
                    buttons: PresetButtons = PresetButtons.INFORMATION) \
            -> 'BrainFrameMessage':
        """Provide a user with some information"""

        message = cls(
            parent=parent,
            title=title,
            text=message,
            subtext=subtext,
            buttons=buttons)
        message.icon = QMessageBox.Information

        return message

    # noinspection PyMethodOverriding
    @classmethod
    def question(cls, parent: QWidget, title: str, question: str,
                 subtext: Optional[str] = None,
                 buttons: PresetButtons = PresetButtons.QUESTION) \
            -> 'BrainFrameMessage':
        """Ask a user a question"""

        message = cls(
            parent=parent,
            title=title,
            text=question,
            subtext=subtext,
            buttons=buttons)
        message.icon = QMessageBox.Question

        return message

    # noinspection PyMethodOverriding
    @classmethod
    def warning(cls, parent: QWidget, title: str, warning: str,
                subtext: Optional[str] = None,
                buttons: PresetButtons = PresetButtons.WARNING) \
            -> 'BrainFrameMessage':
        """Warn a user of an event, occurrence, or otherwise impactful piece of
        information"""

        message = cls(
            parent=parent,
            title=title,
            text=warning,
            subtext=subtext,
            buttons=buttons)
        message.icon = QMessageBox.Warning

        return message

    # noinspection PyMethodOverriding
    @classmethod
    def error(cls, parent: QWidget, title: str, error: str,
              subtext: Optional[str] = None,
              buttons: PresetButtons = PresetButtons.ERROR) \
            -> 'BrainFrameMessage':
        """Display information about a caught exception or other error state
        that has occurred. The client will usually not need to close."""

        message = cls(
            parent=parent,
            title=title,
            text=error,
            subtext=subtext,
            buttons=buttons)
        message.icon = QMessageBox.Critical

        return message

    # noinspection PyMethodOverriding
    @classmethod
    def exception(cls, parent: QWidget, title: str, description: str,
                  traceback: TracebackException,
                  buttons: PresetButtons = PresetButtons.EXCEPTION) \
            -> 'BrainFrameMessage':
        """Display information about an uncaught exception. The client will
        usually need to close"""

        message = cls(
            parent=parent,
            title=title,
            text=description,
            subtext=None,  # Used by traceback
            buttons=buttons)
        message.traceback = traceback

        message.icon = QMessageBox.Critical

        return message

    # noinspection PyMethodOverriding
    @classmethod
    def critical(cls, parent: QWidget, title: str, text: str,
                 traceback: Optional[TracebackException] = None,
                 buttons: PresetButtons = PresetButtons.CRITICAL) \
            -> 'BrainFrameMessage':
        """A critical failure that will usually require the client to close,
        but not an uncaught exception"""

        message = cls(
            parent=parent,
            title=title,
            text=text,
            subtext=None,  # Used by traceback
            buttons=buttons)
        message.traceback = traceback

        message.icon = QMessageBox.Critical

        return message

    @property
    def icon(self) -> QMessageBox.Icon:
        return super().icon()

    @icon.setter
    def icon(self, icon: QMessageBox.Icon):
        self.setIcon(icon)
        self.expand_width()

    @property
    def subtext(self) -> Optional[str]:
        return self._subtext

    @subtext.setter
    def subtext(self, subtext: Optional[str]):
        self._subtext = subtext
        self.setInformativeText(subtext)

        self.expand_width()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self.setText(text)

        self.expand_width()

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title
        self.setWindowTitle(title)

    @property
    def traceback(self) -> Optional[TracebackException]:
        return self._traceback

    @traceback.setter
    def traceback(self, traceback: Optional[TracebackException]):
        self._traceback = traceback

        if traceback:
            traceback_lines = list(traceback.format())

            informative_text = traceback_lines[-1]
            detailed_text = ''.join(traceback_lines)
        else:
            informative_text = ""
            detailed_text = ""

        self.setInformativeText(informative_text)
        self.setDetailedText(detailed_text)

        if traceback:
            self.expand_traceback_height()

        self.expand_width()

    @typing.overload
    def add_button(self, standard_button: QMessageBox.StandardButton,
                   on_click: Optional[Callable] = None) -> QPushButton:
        ...

    @typing.overload
    def add_button(self, button_role: QMessageBox.ButtonRole, text: str,
                   on_click: Optional[Callable] = None) -> QPushButton:
        ...

    @typing.overload
    def add_button(self, button_role: QMessageBox.ButtonRole,
                   button: QAbstractButton,
                   on_click: Optional[Callable] = None) -> QAbstractButton:
        ...

    def add_button(self, *,
                   standard_button: QMessageBox.StandardButton = None,
                   button_role: QMessageBox.ButtonRole = None,
                   text: str = None,
                   button: QAbstractButton = None,
                   on_click: Optional[Callable] = None):
        """QMessageBox is not virtual, so this is the best we got

        This function is to support adding optional on_click slots
        """
        if text:
            button = super().addButton(text, button_role)
        elif button:
            button = super().addButton(button, button_role)
        else:
            button = super().addButton(standard_button)

        if on_click:
            # Disconnect the signals that make the message box close when
            # _any_ button is pressed
            button.clicked.disconnect()
            button.clicked.connect(on_click)

        return button

    def _create_preset_buttons(self, buttons: PresetButtons):
        if not buttons:
            return
        if buttons & self.PresetButtons.OK:
            self.add_button(standard_button=QMessageBox.Ok)
        if buttons & self.PresetButtons.YES:
            self.add_button(standard_button=QMessageBox.Yes)
        if buttons & self.PresetButtons.NO:
            self.add_button(standard_button=QMessageBox.No)
        if buttons & self.PresetButtons.CLOSE_CLIENT:
            button_text = self.tr("Close client")
            button = self.add_button(
                button_role=QMessageBox.DestructiveRole,
                text=button_text,
                on_click=actions.close_client)

            self.setDefaultButton(button)
            self.setEscapeButton(button)

        if buttons & self.PresetButtons.COPY_TO_CLIPBOARD:
            button_text = self.tr("Copy to clipboard")
            self.add_button(button_role=QMessageBox.ActionRole,
                            text=button_text, on_click=self._copy_to_clipboard)
        if buttons & self.PresetButtons.SERVER_CONFIG:
            button_text = self.tr("Server config")
            self.add_button(button_role=QMessageBox.ActionRole,
                            text=button_text,
                            on_click=self._open_server_config)

    def _copy_to_clipboard(self):
        """Copy the message's text to the system clipboard"""
        clipboard = QApplication.clipboard()

        clipboard_text = f"{self.informativeText()}\n\n" \
                         f"{self.detailedText()}"

        clipboard.setText(clipboard_text)

    def _open_server_config(self):
        # Avoid circular imports
        from brainframe_qt.ui.dialogs import ServerConfigurationDialog
        ServerConfigurationDialog.show_dialog(parent=self)
