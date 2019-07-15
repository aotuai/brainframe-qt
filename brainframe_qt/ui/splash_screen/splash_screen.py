from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen, QVBoxLayout, QPushButton

from brainframe.client.ui.dialogs import ServerConfigurationDialog
from brainframe.client.ui.resources.paths import image_paths


class SplashScreen(QSplashScreen):

    def __init__(self):
        pixmap = QPixmap(str(image_paths.splash_screen))

        super().__init__(pixmap=pixmap)

        # Force window to be borderless (like a splashscreen, but also let it
        # have a taskbar icon and be draggable)
        self.setWindowFlags(Qt.FramelessWindowHint)

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

    def showMessage(self, message=None,
                    alignment=Qt.AlignLeft | Qt.AlignBottom,
                    color=Qt.white):
        """Default to show message at bottom left in white"""

        # Change the current message if provided, otherwise just update it
        self.current_message = message or self.current_message

        message = self.message() + ("." * self.num_periods)
        super().showMessage(message, alignment, color)

    def increase_ellipses(self, max_periods=6):
        """Turn the number of periods at the end of the string into a loading
        pattern

        Increases the number of periods until max_periods is reached
        """

        self.num_periods = (self.num_periods + 1) % max_periods
        self.showMessage()

    def show_configuration_button(self):
        self.setLayout(QVBoxLayout())
        button = QPushButton("Configure")
        button.setFocusPolicy(Qt.NoFocus)
        # noinspection PyUnresolvedReferences
        button.clicked.connect(
            lambda: ServerConfigurationDialog.show_dialog(self))

        self.layout().addWidget(button)
        self.layout().setAlignment(button, Qt.AlignBottom | Qt.AlignRight)
