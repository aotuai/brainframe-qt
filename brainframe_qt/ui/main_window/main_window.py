import sys
from pathlib import PosixPath

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget, QSizePolicy
from PyQt5.uic import loadUi

from brainframe.client.api import api, api_errors
from brainframe.client.ui.dialogs import AboutPage, \
    IdentityConfiguration, PluginConfigDialog, RenderConfiguration, \
    ServerConfigurationDialog, StreamConfigurationDialog
from brainframe.client.ui.resources.paths import image_paths, qt_ui_paths
from brainframe.client.ui.resources.ui_elements.buttons import \
    FloatingActionButton


class MainWindow(QMainWindow):
    """Main window for entire UI"""

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi(qt_ui_paths.main_window_ui, self).show()

        self._init_ui()

    def _init_ui(self):

        self._setup_toolbar()

        add_new_stream_button = FloatingActionButton(
            self.video_thumbnail_view,
            self.palette().highlight())
        add_new_stream_button.show()  # No idea why this is necessary
        # noinspection PyUnresolvedReferences
        add_new_stream_button.clicked.connect(self.add_new_stream_slot)
        add_new_stream_button.setToolTip(self.tr("Add new stream"))

        # Add a spacer to make the license button appear right justified
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tool_bar.insertWidget(self.show_about_page_action, spacer)

        # https://stackoverflow.com/a/43835396/8134178
        # 1 : 3 width ratio when expanded
        self.video_splitter.setSizes([self.width() / 3, self.width()])

        self.hide_video_expanded_view()

        # Add the Dilili logo to the bottom right
        self.setStyleSheet(
            f"#centralwidget {{"
            f"    background-image: url({image_paths.background.as_posix()});"
            f"    background-position: right bottom;"
            f"    background-repeat: no-repeat;"
            f"}}")

    def _setup_toolbar(self):
        # Add icons to buttons in toolbar
        video_config_icon = QIcon(str(image_paths.video_settings_icon))
        identity_config_icon = QIcon(str(image_paths.settings_gear_icon))
        plugin_config_icon = QIcon(str(image_paths.global_plugin_conf_icon))
        about_page_icon = QIcon(str(image_paths.information_icon))
        server_configuration_icon = \
            QIcon(str(image_paths.server_configuration_icon))

        self.server_configuration_action.setIcon(server_configuration_icon)
        self.video_configuration_action.setIcon(video_config_icon)
        self.identity_configuration_action.setIcon(identity_config_icon)
        self.plugin_configuration_action.setIcon(plugin_config_icon)
        self.show_about_page_action.setIcon(about_page_icon)

    @pyqtSlot()
    def show_video_expanded_view(self):
        """Called by thumbnail_view when a thumbnail is clicked"""
        self.video_expanded_view.setHidden(False)

    @pyqtSlot()
    def hide_video_expanded_view(self):
        """Called by expanded_view when expanded video is closed"""
        self.video_expanded_view.setHidden(True)

    @pyqtSlot()
    def show_server_configuration_dialog_slot(self):
        ServerConfigurationDialog.show_dialog(self)

    @pyqtSlot()
    def add_new_stream_slot(self):
        """Open dialog to add a new stream and then send it to the server"""

        stream_conf = StreamConfigurationDialog.configure_stream(self)
        if stream_conf is None:
            return
        try:
            stream_conf = api.set_stream_configuration(stream_conf)

            # Currently, we default to setting all new streams as 'active'
            api.start_analyzing(stream_conf.id)

            self.video_thumbnail_view.new_stream(stream_conf)
        except api_errors.DuplicateStreamSourceError as err:
            message_title = self.tr("Error Opening Stream")
            message_desc = self.tr("Stream source already open")
            message_info = self.tr("You already have the stream source open.")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{message_info}<br><br>" \
                      f"{error_text}<b>{err.kind}</b>"

            QMessageBox.information(self, message_title, message)
        except api_errors.StreamNotOpenedError as err:
            message_title = self.tr("Error Opening Stream")
            message_desc = self.tr("Error encountered while opening stream")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{err}<br><br>" \
                      f"{err.description}<br><br>" \
                      f"{error_text}<b>{err.kind}</b>"
            QMessageBox.information(self, message_title, message)
        except api_errors.AnalysisLimitExceededError:
            # Delete the stream configuration, since you almost never want to
            # have a stream that can't have analysis running
            api.delete_stream_configuration(stream_conf.id)

            message_title = self.tr("Error Opening Stream")
            message_desc = self.tr("Active Stream Limit Exceeded")
            message_info1 = self.tr(
                "You have exceeded the number of active streams available to "
                "you under the terms of your license. Consider deleting "
                "another stream or contacting Aotu to increase your "
                "active stream limit.")
            message = (f"<b>{message_desc}</b>"
                       f"<br><br>"
                       f"{message_info1}")
            QMessageBox.information(self, message_title, message)
        except api_errors.BaseAPIError as err:
            message_title = self.tr("Error Opening Stream")
            message_desc = self.tr("Error encountered while opening stream")
            message_info1 = self.tr("Is stream already open?")
            message_info2 = self.tr("Is this a valid stream source?")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{message_info1}<br>" \
                      f"{message_info2}<br><br>" \
                      f"{error_text}<b>{err.kind}</b>"
            QMessageBox.information(self, message_title, message)

    @pyqtSlot()
    def show_video_configuration_dialog(self):
        RenderConfiguration.show_dialog(self)

    @pyqtSlot()
    def show_identities_dialog(self):
        IdentityConfiguration.show_dialog(self)

    @pyqtSlot()
    def show_about_page_dialog(self):
        AboutPage.show_dialog(self)

    @pyqtSlot()
    def show_global_plugin_config_dialog(self):
        PluginConfigDialog.show_dialog(self)
