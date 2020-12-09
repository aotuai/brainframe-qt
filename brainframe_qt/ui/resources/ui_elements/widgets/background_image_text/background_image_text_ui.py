from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

# noinspection PyUnresolvedReferences
from brainframe_qt.ui.resources import qt_resources, stylesheet_watcher
from brainframe_qt.ui.resources.ui_elements.widgets import \
    AspectRatioSVGWidget


class BackgroundImageTextUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.image = self._init_image()
        self.text_label = self._init_text_label()

        self._init_layout()
        self._init_style()

    def _init_image(self) -> AspectRatioSVGWidget:
        image = AspectRatioSVGWidget(":/icons/alert", self)
        image.setObjectName("background_image")

        image.alignment = Qt.AlignBottom | Qt.AlignHCenter

        return image

    def _init_text_label(self) -> QLabel:
        text_label = QLabel("[Text]", self)
        text_label.setObjectName("text_label")

        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)

        return text_label

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # These stretch values are very arbitrary
        layout.addStretch(stretch=2)
        layout.addWidget(self.image, stretch=6)
        layout.addWidget(self.text_label, stretch=1)
        layout.addStretch(stretch=1)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)
