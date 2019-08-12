import sys

from PyQt5.QtCore import QSettings

_settings = QSettings(
    # MacOS uses internet domain instead of organization name
    'dilililabs.com' if sys.platform == 'darwin' else 'dilili-labs',
    'brainframe')


class Setting:
    """A small wrapper around QSettings that holds the name, type, and default,
    and also allows you to 'import' settings around the project without having
    to worry about keeping the name the same everywhere. It also helps refactor.
    """

    def __init__(self, default, type_, name):
        """Set the default if it doesn't exist yet"""
        self.default = default
        self.type = type_
        self.name = name
        self._cache = None

        # Record the setting officially if they don't exist yet
        if default is not None and _settings.value(name) is None:
            self.set(self.default)

    def set(self, value):
        _settings.setValue(self.name, value)
        self._cache = value

    def val(self):
        if self._cache is None:
            self._cache = _settings.value(self.name, type=self.type)
        return self._cache

    def delete(self):
        _settings.remove(self.name)
        self._cache = None


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

# License settings
client_license_accepted = Setting(
    False, type_=bool, name="client_license_accepted")
client_license_md5 = Setting(
    None, type_=str, name="client_license_md5")

# Render Configuration Settings
draw_lines = Setting(
    True, type_=bool, name="video_draw_lines")
draw_regions = Setting(
    True, type_=bool, name="video_draw_regions")
draw_detections = Setting(
    True, type_=bool, name="video_draw_detections")
use_polygons = Setting(
    True, type_=bool, name="video_use_polygons")
show_detection_tracks = Setting(
    True, type_=bool, name="video_show_tracks")
show_recognition_confidence = Setting(
    True, type_=bool, name="video_show_confidence")
show_detection_labels = Setting(
    True, type_=bool, name="video_show_detection_labels")
show_attributes = Setting(
    True, type_=bool, name="video_show_attributes")
