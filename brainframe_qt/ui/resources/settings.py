import sys
from typing import Generic, Optional, TypeVar, Type

from PyQt5.QtCore import QSettings, QObject, pyqtSignal

T = TypeVar("T")

_settings = QSettings(
    # MacOS uses internet domain instead of organization name
    'aotu.ai' if sys.platform == 'darwin' else 'aotu',
    'brainframe')


class Setting(QObject, Generic[T]):
    value_changed = pyqtSignal(object)
    value_deleted = pyqtSignal()

    def __init__(self, name: str, default: T, type_: Type[T]):
        super().__init__()
        self.name = name
        self.default = default
        self.type = type_

        self._cache: Optional[T] = None

    def __set__(self, instance: object, value: T) -> None:
        prev_value = self._cache

        _settings.setValue(self.name, value)
        self._cache = value

        if value != prev_value:
            self.value_changed.emit(value)

    def __get__(self, instance, owner) -> T:
        if self._cache is not None:
            return self._cache

        return _settings.value(self.name, defaultValue=self.default, type=self.type)

    def __delete__(self, instance: object) -> None:
        prev_value = self._cache

        _settings.remove(self.name)
        self._cache = None

        if prev_value is not None:
            self.value_changed.emit(None)
            self.value_deleted.emit()


class SettingsManager(QObject):
    value_changed = pyqtSignal(str, object)
    value_deleted = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Search for the descriptor on the class
        # https://stackoverflow.com/a/3681323/8134178
        for cls in [self] + self.__class__.mro():
            for obj in cls.__dict__.values():
                if isinstance(obj, Setting):
                    obj.value_changed.connect(self._on_value_changed)
                    obj.value_deleted.connect(self._on_value_deleted)

    def _on_value_changed(self, value) -> None:
        sender: Setting = self.sender()  # type: ignore
        self.value_changed.emit(sender.name, value)

    def _on_value_deleted(self):
        sender: Setting = self.sender()  # type: ignore
        self.value_deleted.emit(sender.name)
