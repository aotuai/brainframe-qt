from PyQt5.QtCore import QSettings

_settings = QSettings()


class Setting:
    """A small wrapper around QSettings that holds the name, type, and default,
    and also allows you to 'import' settings around the project without having
    to worry about keeping the name the same everywhere. It also helps refactor.
    """

    def __init__(self, default, type, name):
        """Set the default if it doesn't exist yet"""
        self.default = default
        self.type = type
        self.name = name

        # Record the setting officially if they don't exist yet
        if default is not None and _settings.value(name) is None:
            self.set(self.default)

    def set(self, value):
        _settings.setValue(self.name, value)

    def val(self):
        return _settings.value(self.name, type=self.type)


# License settings
client_license_accepted = Setting(
    False, type=bool, name="client_license_accepted")
client_license_md5 = Setting(
    None, type=str, name="client_license_md5")

# Video Configuration Settings
draw_lines = Setting(
    True, type=bool, name="video_draw_lines")
draw_regions = Setting(
    True, type=bool, name="video_draw_regions")
draw_detections = Setting(
    True, type=bool, name="video_draw_detections")
use_polygons = Setting(
    True, type=bool, name="video_use_polygons")
show_detection_tracks = Setting(
    True, type=bool, name="video_show_tracks")
show_recognition_confidence = Setting(
    True, type=bool, name="video_show_confidence")
show_detection_labels = Setting(
    True, type=bool, name="video_show_detection_labels")
show_attributes = Setting(
    True, type=bool, name="video_show_attributes")
