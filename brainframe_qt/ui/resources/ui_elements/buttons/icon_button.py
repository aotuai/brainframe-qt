from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QPushButton, QStyleOptionButton, QStyle, \
    QStylePainter


class TextIconButton(QPushButton):
    """Button primarily for displaying emojis as if they were icons

    This class fixes a problem with the width of the button not matching the
    the text if the text is very short.

    It also forces mouse hovering to still have a visual effect even if the
    button is flat
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.flat: bool = super().isFlat()
        """Store whether or not we want the button to be flat. 
        Real flatness temporarily changes when mouse is hovering in self.event
        """

        self._fix_button_width()

    def event(self, event: QEvent) -> bool:

        if self.isFlat():
            # Still change color when hovered over, even if flat
            # From docs for `flat` attribute:
            # "If this property is set, most styles will not paint the button
            #  background unless the button is being pressed."
            if event.type() == QEvent.HoverEnter:
                super().setFlat(False)
            if event.type() == QEvent.HoverLeave:
                super().setFlat(True)

        return super().event(event)

    def isFlat(self) -> bool:
        return self.flat

    def setFlat(self, flat: bool):
        self.flat = flat
        super().setFlat(flat)

    def _fix_button_width(self):
        """Set min width of button properly

        # https://stackoverflow.com/a/19502467/8134178
        """
        text_size = self.fontMetrics().size(Qt.TextShowMnemonic, self.text())
        options = QStyleOptionButton()
        options.initFrom(self)
        options.rect.setSize(text_size)
        button_size = self.style().sizeFromContents(
            QStyle.CT_PushButton,
            options,
            text_size,
            self)

        # Width at minimum should make button square
        button_size.setWidth(max(button_size.width(), button_size.height()))

        self.setMaximumSize(button_size)
