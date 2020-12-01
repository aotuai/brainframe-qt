from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.uic import loadUi

from brainframe_qt.extensions import DialogActivity
from brainframe_qt.ui.resources import settings
from brainframe_qt.ui.resources.config import QSettingsRenderConfig
from brainframe_qt.ui.resources.paths import qt_ui_paths


class ClientConfigActivity(DialogActivity):

    _built_in = True

    def open(self, *, parent: QWidget):
        RenderConfiguration.show_dialog(parent=parent)

    def window_title(self) -> str:
        return QApplication.translate("ClientConfigActivity",
                                      "Client Configuration")

    @staticmethod
    def icon() -> QIcon:
        return QIcon(":/icons/client_config")

    @staticmethod
    def short_name() -> str:
        return QApplication.translate("ClientConfigActivity", "Client")


class RenderConfiguration(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi(qt_ui_paths.client_configuration_ui, self)

        self.render_config = QSettingsRenderConfig()

        self.detections_checkbox.setChecked(self.render_config.draw_detections)
        self.polygon_radio_button.setChecked(self.render_config.use_polygons)
        self.bbox_radio_button.setChecked(not self.render_config.use_polygons)
        self.detection_labels_checkbox.setChecked(
            self.render_config.show_detection_labels)
        self.detection_attributes_checkbox.setChecked(
            self.render_config.show_attributes)
        self.regions_checkbox.setChecked(self.render_config.draw_regions)
        self.lines_checkbox.setChecked(self.render_config.draw_lines)
        self.tracks_checkbox.setChecked(
            self.render_config.show_detection_tracks)
        self.recognition_checkbox.setChecked(
            self.render_config.show_recognition_labels)
        self.extra_data_checkbox.setChecked(self.render_config.show_extra_data)

    @classmethod
    def show_dialog(cls, parent):
        ...

        dialog = cls(parent)

        result = dialog.exec_()
        if not result:
            return

        # Get new values from the UI
        _detection_display_type = dialog.detection_radio_group.checkedButton()
        use_polygons = _detection_display_type is dialog.polygon_radio_button

        # Change the settings
        dialog.render_config.draw_regions = dialog.regions_checkbox.isChecked()
        dialog.render_config.draw_lines = dialog.lines_checkbox.isChecked()
        dialog.render_config.draw_detections \
            = dialog.detections_checkbox.isChecked()
        dialog.render_config.use_polygons = use_polygons
        dialog.render_config.show_detection_labels \
            = dialog.detection_labels_checkbox.isChecked()
        dialog.render_config.show_attributes \
            = dialog.detection_attributes_checkbox.isChecked()
        dialog.render_config.show_detection_tracks \
            = dialog.tracks_checkbox.isChecked()
        dialog.render_config.show_recognition_labels \
            = dialog.recognition_checkbox.isChecked()
        dialog.render_config.show_extra_data \
            = dialog.extra_data_checkbox.isChecked()

        dialog.render_config.save_to_disk()
