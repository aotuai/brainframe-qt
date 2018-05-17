from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen

from visionapp.client.ui.resources.paths import image_paths


class SplashScreen(QSplashScreen):

    def __init__(self):
        pixmap = QPixmap(str(image_paths.splash_screen))

        super().__init__(pixmap=pixmap, flags=Qt.WindowStaysOnTopHint)

        # Make the number of ellipses pulse
        self.ellipses_timer = QTimer()
        # noinspection PyUnresolvedReferences
        # connect is erroneously detected as unresolved
        self.ellipses_timer.timeout.connect(self.increase_ellipses)
        self.ellipses_timer.start(1000)

        # Keep the splash screen on top in window managers that do not support
        # always on top flag
        self.raise_timer = QTimer()
        # noinspection PyUnresolvedReferences
        # connect is erroneously detected as unresolved
        self.raise_timer.timeout.connect(self.raise_)
        self.raise_timer.start(10)

    def __enter__(self):
        self.show()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ellipses_timer.stop()
        self.raise_timer.stop()

    def increase_ellipses(self, max_periods=6):
        """Turn the number of periods at the end of the string into a loading
        pattern

        Increases the number of periods until max_periods is reached
        """
        current_message = self.message()
        num_periods = len(current_message) - len(current_message.rstrip('.'))

        num_periods = (num_periods + 1) % (max_periods + 1)

        self.showMessage(current_message.rstrip('.') + '.' * num_periods)

    def showMessage(self, message,
                    alignment=Qt.AlignLeft | Qt.AlignBottom,
                    color=Qt.white):
        """Default to show message at bottom left in white"""
        super().showMessage(message, alignment, color)

    def mousePressEvent(self, event):
        """Don't do anything on click. Default option is to hide"""
        pass
