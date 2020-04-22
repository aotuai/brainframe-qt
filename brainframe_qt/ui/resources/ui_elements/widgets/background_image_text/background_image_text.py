from PyQt5.QtWidgets import QWidget

from brainframe.client.ui.resources.ui_elements.widgets.background_image_text \
    .background_image_text_ui import BackgroundImageTextUI


class BackgroundImageText(BackgroundImageTextUI):
    def __init__(self, text: str, svg_path: str, parent: QWidget):
        super().__init__(parent)

        self.text = text
        self.svg_path = svg_path

    @property
    def text(self) -> str:
        return self.text_label.text()

    @text.setter
    def text(self, text: str):
        self.text_label.setText(text)

    @property
    def svg_path(self):
        # Only setter
        raise NotImplementedError

    @svg_path.setter
    def svg_path(self, svg_path: str):
        self.image.load(svg_path)


if __name__ == '__main__':
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QDesktopWidget

    # noinspection PyArgumentList
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication([])

    # noinspection PyArgumentList
    window = QWidget()
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.resize(QDesktopWidget().availableGeometry(window).size() * .4)
    window.setAttribute(Qt.WA_StyledBackground, True)

    window.setLayout(QVBoxLayout())
    window.layout().addWidget(
        BackgroundImageText("No alerts", ":/icons/alert", None))

    window.show()

    app.exec_()
