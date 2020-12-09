from typing import Optional

from PyQt5.QtWidgets import QProxyStyle, QStyleOption, QStyleHintReturn, \
    QWidget

from brainframe_qt.ui.resources.mixins import BaseWidgetMixin


class TransientScrollbarMI(BaseWidgetMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyle(_TransientScrollBarStyle())


class _TransientScrollBarStyle(QProxyStyle):

    def __init__(self, base_style: Optional[QProxyStyle] = None, *args):
        super().__init__(*args)
        self._base_style = base_style or super()

    def styleHint(self, style_hint, option: QStyleOption = None,
                  widget: QWidget = None,
                  return_data: QStyleHintReturn = None) -> int:

        if style_hint == QProxyStyle.SH_ScrollBar_Transient:
            return int(True)
        else:
            return self._base_style \
                .styleHint(style_hint, option, widget, return_data)
