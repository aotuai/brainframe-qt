from PyQt5.QtGui import QColor


# TODO: Remove when using a recent-enough version of Qt to get QColorConstants
class QColorConstants:
    Black = QColor(0, 0, 0)
    Green = QColor(0, 255, 0)
    Red = QColor(255, 0, 0)
    Transparent = QColor(0, 0, 0, 0)
    White = QColor(255, 255, 255)

    class Svg:
        orange = QColor(255, 165, 0)
