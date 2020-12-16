from typing import List, Set

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget

# TODO: This is way too nested. Potentially make Alerts a more "generic" item
from brainframe_qt.ui.main_window.video_expanded_view.video_large.stream_overlay import \
    AbstractOverlayAlert
from .stream_alert import StreamAlert


class OverlayTray(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self.alert_widgets: Set[StreamAlert] = set()

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

    def handle_alerts(self, alerts: List[AbstractOverlayAlert]) -> None:
        # Calculate which alerts we need to create and which we need to remove
        widgets_to_remove = self.alert_widgets.copy()
        alerts_to_add = alerts.copy()
        all_widgets: List[StreamAlert] = []

        # Iterate over all current alert widgets
        for alert_widget in self.alert_widgets:

            # If we see an alert widget we need an alert for
            if alert_widget.alert in alerts_to_add:
                widgets_to_remove.remove(alert_widget)

                # Also don't create a new alert
                alerts_to_add.remove(alert_widget.alert)

                # Keep track of it
                all_widgets.append(alert_widget)

                # Refresh the widget's timeout
                alert_widget.refresh_timeout()

        # Remove the unneeded widgets
        for alert_widget in widgets_to_remove:
            # Don't remove widget if it hasn't been on screen for long enough
            if not alert_widget.past_minimum_duration:
                continue

            self.layout().removeWidget(alert_widget)
            alert_widget.deleteLater()

            self.alert_widgets.remove(alert_widget)

        # Add the new ones
        for alert in alerts_to_add:
            alert_widget = StreamAlert(alert, parent=self)
            self.layout().addWidget(alert_widget)

            self.alert_widgets.add(alert_widget)
