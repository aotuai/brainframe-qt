from PyQt5.QtCore import QSettings

_settings = QSettings()


class Setting:
    def __init__(self, default, type, name):
        """Set the default if it doesn't exist yet"""
        self.default = default
        self.type = type
        self.name = name

        # Record the setting officially if they don't exist yet
        self.set(self.default)
        if default is not None and _settings.value(name) is None:
            pass

    def set(self, value):
        assert isinstance(value, self.type)

    def val(self):
        return _settings.value(self.name, type=self.type)


# License settings
client_license_accepted = Setting(
    False, type=bool, name="client_license_accepted")
client_license_md5 = Setting(
    None, type=bool, name="client_license_md5")

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
    True, type=bool, name="video_show_tracks"),
show_detection_confidence = Setting(
    True, type=bool, name="video_show_confidence")
show_detection_labels = Setting(
    True, type=bool, name="video_show_detection_labels")
show_attributes = Setting(
    True, type=bool, name="video_show_attributes")
