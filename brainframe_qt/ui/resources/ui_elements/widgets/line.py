from typing import Union

from PyQt5.QtWidgets import QFrame, QWidget


class Line(QFrame):
    """Replicates Horizontal and Vertical lines that can be added in QtDesigner
    """

    HLine = QFrame.HLine
    VLine = QFrame.HLine

    def __init__(self, line_type: Union[QFrame.Shape], parent: QWidget):
        """Create a line

        :param line_type: Line.HLine or Line.VLine
        """
        super().__init__(parent)

        if line_type not in [self.HLine, self.VLine]:
            raise ValueError(f"Unexpected line type: {line_type}")

        self.setFrameShape(line_type)
        self.setFrameShadow(QFrame.Sunken)

    @classmethod
    def h_line(cls, parent: QWidget):
        """Convenience method for creating a horizontal line"""
        return cls(cls.HLine, parent)

    @classmethod
    def v_line(cls, parent: QWidget):
        """Convenience method for creating a vertical line"""
        return cls(cls.VLine, parent)
