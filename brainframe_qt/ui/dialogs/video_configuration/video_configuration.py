from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSettings

from brainframe.client.ui.resources.paths import qt_ui_paths

# Keys for different QSettings
VIDEO_DRAW_REGIONS = "video_show_zones"
VIDEO_DRAW_LINES = "video_show_lines"
VIDEO_DRAW_DETECTIONS = "video_show_detections"
VIDEO_USE_POLYGONS = "video_use_polygons"
VIDEO_SHOW_DETECTION_LABELS = "video_show_detection_labels"
VIDEO_SHOW_ATTRIBUTES = "video_show_attributes"


class VideoConfiguration(QDialog):
    # Default settings
    draw_lines = True
    draw_regions = True
    draw_detections = True
    use_polygons = True
    show_detection_labels = True
    show_attributes = True

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi(qt_ui_paths.video_configuration_ui, self)

        self._settings = QSettings()

        # Detections
        draw_detections = self._settings.value(
            VIDEO_DRAW_DETECTIONS,
            type=bool)
        use_polygons = self._settings.value(
            VIDEO_USE_POLYGONS,
            type=bool)
        show_detection_labels = self._settings.value(
            VIDEO_SHOW_DETECTION_LABELS,
            type=bool)
        show_attributes = self._settings.value(
            VIDEO_SHOW_ATTRIBUTES,
            type=bool)

        # Regions
        draw_regions = self._settings.value(
            VIDEO_DRAW_REGIONS,
            type=bool)

        # Lines
        draw_lines = self._settings.value(
            VIDEO_DRAW_LINES,
            type=bool)

        self.detections_checkbox.setChecked(draw_detections)
        self.polygon_radio_button.setChecked(use_polygons)
        self.bbox_radio_button.setChecked(not use_polygons)
        self.detection_labels_checkbox.setChecked(show_detection_labels)
        self.detection_attributes_checkbox.setChecked(show_attributes)
        self.regions_checkbox.setChecked(draw_regions)
        self.lines_checkbox.setChecked(draw_lines)

    @classmethod
    def show_dialog(cls):
        ...

        dialog = cls()

        result = dialog.exec_()
        if not result:
            return

        # Detections
        draw_detections = dialog.detections_checkbox.isChecked()
        _detection_display_type = dialog.detection_radio_group.checkedButton()
        use_polygons = _detection_display_type is dialog.polygon_radio_button
        show_detection_labels = dialog.detection_labels_checkbox.isChecked()
        show_attributes = dialog.detection_attributes_checkbox.isChecked()

        # Regions
        draw_regions = dialog.regions_checkbox.isChecked()

        # Lines
        draw_lines = dialog.lines_checkbox.isChecked()

        dialog._settings.setValue(VIDEO_DRAW_LINES, draw_lines)
        dialog._settings.setValue(VIDEO_DRAW_REGIONS, draw_regions)
        dialog._settings.setValue(VIDEO_DRAW_DETECTIONS, draw_detections)
        dialog._settings.setValue(VIDEO_USE_POLYGONS, use_polygons)
        dialog._settings.setValue(VIDEO_SHOW_DETECTION_LABELS,
                                  show_detection_labels)
        dialog._settings.setValue(VIDEO_SHOW_ATTRIBUTES, show_attributes)


    @classmethod
    def initialize_settings(cls):
        settings = QSettings()
        if settings.value(VIDEO_DRAW_DETECTIONS) is None:
            cls.set_default_settings()

    @classmethod
    def set_default_settings(cls):
        settings = QSettings()

        settings.setValue(VIDEO_DRAW_LINES, cls.draw_lines)
        settings.setValue(VIDEO_DRAW_REGIONS, cls.draw_regions)
        settings.setValue(VIDEO_DRAW_DETECTIONS, cls.draw_detections)
        settings.setValue(VIDEO_USE_POLYGONS, cls.use_polygons)
        settings.setValue(VIDEO_SHOW_DETECTION_LABELS,
                          cls.show_detection_labels)
        settings.setValue(VIDEO_SHOW_ATTRIBUTES, cls.show_attributes)
