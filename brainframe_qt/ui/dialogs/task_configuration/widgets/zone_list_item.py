from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget

from brainframe.api import bf_codecs

from ..core.zone import Line, Region, Zone
from ..widgets.zone_list_item_ui import ZoneListItemUI, ZoneListType


class ZoneListZoneItem(ZoneListItemUI):

    zone_delete = pyqtSignal(int)
    zone_edit = pyqtSignal(int)
    zone_name_change = pyqtSignal(int, str)

    def __init__(self, zone: Zone, *, parent: QObject):
        super().__init__(parent=parent)

        self._zone = zone

        self.entry_name = zone.name
        self.entry_type = self._get_entry_type(zone)

        self._init_signals()
        self._configure_buttons()

    def _init_signals(self) -> None:
        self.trash_button.clicked.connect(self._on_trash_button_click)
        self.edit_button.clicked.connect(self._on_edit_button_click)
        self.name_label.text_changed.connect(self._on_zone_name_change)

    def _configure_buttons(self) -> None:
        if self._zone.name == bf_codecs.Zone.FULL_FRAME_ZONE_NAME:
            self.trash_button.setDisabled(True)
            self.edit_button.setDisabled(True)

    def _on_edit_button_click(self, _clicked: bool) -> None:
        self.zone_edit.emit(self._zone.id)

    def _on_trash_button_click(self, _clicked: bool) -> None:
        self.zone_delete.emit(self._zone.id)

    def _on_zone_name_change(self, zone_name: str) -> None:
        self.zone_name_change.emit(self._zone.id, zone_name)

    @staticmethod
    def _get_entry_type(zone: Zone) -> ZoneListType:
        if isinstance(zone, Line):
            return ZoneListType.LINE
        elif isinstance(zone, Region):
            return ZoneListType.REGION
        else:
            return ZoneListType.UNKNOWN


class ZoneListAlarmItem(ZoneListItemUI):
    """Temporary until ZoneListZoneItem holds Alarm widgets"""
    alarm_delete = pyqtSignal(int)

    def __init__(self, alarm: bf_codecs.ZoneAlarm, *, parent: QObject):
        super().__init__(parent=parent)

        self._padding_widget = self._init_padding_widget()

        self._alarm = alarm

        self.entry_name = alarm.name
        self.entry_type = ZoneListType.ALARM

        self._init_signals()

    def _init_signals(self) -> None:
        self.trash_button.clicked.connect(self._on_trash_button_click)

    def _init_padding_widget(self) -> QWidget:
        """Temporary solution to indent alarm widgets a bit.

        Stylesheet controls width
        """
        widget = QWidget(self)
        widget.setObjectName("padding_widget")

        self.layout().insertWidget(0, widget)

        return widget

    def _on_trash_button_click(self, _clicked: bool) -> None:
        self.alarm_delete.emit(self._alarm.id)
