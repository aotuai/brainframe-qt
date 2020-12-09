import sys
import typing
from enum import Enum
from typing import Any

import pendulum
from PyQt5.QtCore import QSettings
from pendulum.tz.timezone import Timezone
from pubsus import PubSubMixin


class Setting(PubSubMixin):
    """A small wrapper around QSettings that holds the name, type, and default,
    and also allows you to 'import' settings around the project without having
    to worry about keeping the name the same everywhere. It also helps refactor.
    """
    _settings = QSettings(
        # MacOS uses internet domain instead of organization name
        'aotu.ai' if sys.platform == 'darwin' else 'aotu',
        'brainframe')

    def __init__(self, default, type_, name):
        """Set the default if it doesn't exist yet"""
        super().__init__()

        self.default = default
        self.type = type_
        self.name = name
        self._cache = None

        # Record the setting officially if they don't exist yet
        if default is not None and self._settings.value(name) is None:
            self.set(self.default)

    def set(self, value):
        self._settings.setValue(self.name, value)
        self._cache = value
        self.publish(Topic.CHANGED, value)

    def val(self):
        if self._cache is None:
            self._cache = self._settings.value(self.name,
                                               defaultValue=self.default,
                                               type=self.type)
        return self._cache

    def delete(self):
        self._settings.remove(self.name)
        self._cache = None


class Topic(Enum):
    CHANGED = "changed"


# TODO: Having to pass in a settings_object is less than ideal
class QSettingsConfig:

    def __init__(self, settings_object):
        super().__setattr__("_settings", settings_object)
        super().__setattr__("_overrides", {})

    def __getattribute__(self, item: str) -> Any:
        if item not in typing.get_type_hints(type(self)):
            return super().__getattribute__(item)

        _overrides = super().__getattribute__("_overrides")
        try:
            return _overrides[item]
        except KeyError:
            _settings = super().__getattribute__("_settings")
            return getattr(_settings, item).val()

    def __setattr__(self, key: str, value: Any):
        if key not in typing.get_type_hints(type(self)):
            raise AttributeError(f"Unknown option '{key}'")

        _overrides = super().__getattribute__("_overrides")
        _overrides[key] = value

    def save_to_disk(self):
        _settings = super().__getattribute__("_settings")
        _overrides = super().__getattribute__("_overrides")

        for key, value in _overrides.items():
            settings_item: Setting = getattr(_settings, key)
            settings_item.set(value)


# System configuration settings
server_url = Setting(
    "http://localhost", type_=str, name="server_url"
)
server_username = Setting(
    None, type_=str, name="server_username"
)
server_password = Setting(
    None, type_=bytes, name="server_password"
)
# Defines what timezone the user wants times to be displayed in. If this value
# is an empty string, the current system timezone will be selected.
user_timezone = Setting(
    "", type_=str, name="user_timezone"
)

# License settings
client_license_accepted = Setting(
    False, type_=bool, name="client_license_accepted"
)
client_license_md5 = Setting(
    None, type_=str, name="client_license_md5"
)

# The maximum size of the frame buffer used for all streams
frame_buffer_size = Setting(
    300, type_=int, name="frame_buffer_size"
)


def get_user_timezone() -> Timezone:
    """Gets the timezone the user should be displayed times in as a Pendulum
    timezone. By default, this is the system timezone.

    :return: The currently configured timezone
    """
    if user_timezone.val() == "":
        # Default to the current timezone
        return pendulum.now().timezone
    else:
        return pendulum.timezone(user_timezone.val())
