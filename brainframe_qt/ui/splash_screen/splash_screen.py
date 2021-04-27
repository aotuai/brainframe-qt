from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QCloseEvent
from PyQt5.QtWidgets import QSplashScreen, QVBoxLayout, QPushButton

from brainframe_qt.ui.dialogs import ServerConfigurationDialog
from brainframe_qt.ui.resources import qt_resources


class SplashScreen(QSplashScreen):

    manually_closed = pyqtSignal()

    def __init__(self):
        pixmap = QPixmap(":/images/splash_screen_png")

        super().__init__(pixmap=pixmap)

        # Force window to be borderless (like a splashscreen, but also let it
        # have a taskbar icon and be draggable)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        self.current_message = super().message()
        """Message without the ellipses"""

        # Make the number of ellipses pulse
        self.num_periods = 0
        self.ellipses_timer = QTimer()
        # noinspection PyUnresolvedReferences
        self.ellipses_timer.timeout.connect(self.increase_ellipses)
        self.ellipses_timer.start(1000)

        # Display a config button if the server hasn't connected for too long
        QTimer.singleShot(3000, self.show_configuration_button)

    def __enter__(self):
        self.show()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ellipses_timer.stop()
        # self.raise_timer.stop()

    def message(self):
        """Message without the ellipses"""
        return self.current_message

    def mousePressEvent(self, event):
        """Don't do anything on click. Default option is to hide"""
        pass

    def showMessage(self, message=None,
                    alignment=Qt.AlignLeft | Qt.AlignBottom,
                    color=Qt.white):
        """Default to show message at bottom left in white"""

        # Change the current message if provided, otherwise just update it
        self.current_message = message or self.current_message

        message = self.message() + (self.tr(".") * self.num_periods)
        super().showMessage(message, alignment, color)

    def closeEvent(self, event: QCloseEvent) -> None:
        # If we receive a closeEvent that is spontaneous, that means the event
        # originated outside of Qt (e.g. from the window manager). This is used to
        # kill the entire client if the splashscreen is intentionally closed by the user.
        if event.spontaneous():
            self.manually_closed.emit()
        super().closeEvent(event)

    def increase_ellipses(self, max_periods=6):
        """Turn the number of periods at the end of the string into a loading
        pattern

        Increases the number of periods until max_periods is reached
        """

        self.num_periods = (self.num_periods + 1) % max_periods
        self.showMessage()

    def show_configuration_button(self):
        self.setLayout(QVBoxLayout())
        button = QPushButton(self.tr("Configure"))
        button.setFocusPolicy(Qt.NoFocus)
        button.clicked.connect(self._open_server_config)

        self.layout().addWidget(button)
        self.layout().setAlignment(button, Qt.AlignBottom | Qt.AlignRight)

    def _open_server_config(self) -> None:
        ServerConfigurationDialog.show_dialog(parent=self)


# Import has side-effects
_ = qt_resources
