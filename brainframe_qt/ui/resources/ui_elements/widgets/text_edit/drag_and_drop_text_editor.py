from pathlib import Path
from typing import Optional, Union

from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent

from .placeholder_text_edit import PlaceholderTextEdit


class DragAndDropTextEditor(PlaceholderTextEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if self._is_valid_drag_drop_event(event):
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if self._is_valid_drag_drop_event(event):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if not self._is_valid_drag_drop_event(event):
            return

        data = event.mimeData()

        path = self._mime_data_file(data)
        if path is not None:
            self.setPlainText(path.read_text())
            return

        text = self._mime_data_text(data)
        if text is not None:
            self.setPlainText(text)

    @classmethod
    def _is_valid_drag_drop_event(cls, event: Union[QDragEnterEvent,
                                                    QDragMoveEvent,
                                                    QDropEvent]) \
            -> bool:

        data = event.mimeData()
        if cls._mime_data_file(data) is not None:
            return True
        if cls._mime_data_text(data) is not None:
            return True

        return False

    @staticmethod
    def _mime_data_file(data: QMimeData) -> Optional[Path]:
        if not data.hasUrls():
            return None

        # Only accept one url
        urls = data.urls()
        if len(urls) != 1:
            return None

        # Only accept files
        url = urls[0]
        if url.scheme() != 'file':
            return None

        return Path(url.toLocalFile())

    @staticmethod
    def _mime_data_text(data: QMimeData) -> Optional[str]:
        # TODO: There's a bug here with .text(). Issue sent to mailing list
        #       https://www.riverbankcomputing.com/pipermail/pyqt/2020-June/042999.html
        if not data.hasText():
            return None

        return data.text()
