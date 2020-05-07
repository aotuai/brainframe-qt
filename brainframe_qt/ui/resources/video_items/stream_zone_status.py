from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

from brainframe.api import codecs
from brainframe.client.ui.resources.video_items import StreamPolygon, \
    StreamLabelBox


class ZoneStatusPolygon(StreamPolygon):
    """Render a ZoneStatus's Zone along with information about the Zone
    Status"""
    NORMAL_COLOR = QColor(0, 255, 125)
    ALERTING_COLOR = QColor(255, 125, 0)

    def __init__(self, status: codecs.ZoneStatus, text_size, *,
                 border_thickness=1, parent=None):

        # Find the top-left point of the zone
        top_left = sorted(status.zone.coords,
                          key=lambda pt: pt[0] ** 2 + pt[1] ** 2)[0]

        # Create the description box for the zone
        text = status.zone.name
        if len(status.zone.coords) == 2:
            # If the zone is a line
            if len(status.total_entered):
                entering_text = QApplication.translate(
                    "ZoneStatusPolygon",
                    "Entering: ")
                entering_counts = ", ".join(
                    ["{} {}{}".format(count, class_name, "s" * bool(count - 1))
                     for class_name, count in status.total_entered.items()
                     if count > 0])

                if len(entering_counts):
                    text += f"\n{entering_text}{entering_counts}"

            if len(status.total_exited):
                exiting_text = QApplication.translate(
                    "ZoneStatusPolygon",
                    "Exiting: ")
                exiting_counts = ", ".join(
                    ["{} {}{}".format(count, class_name, "s" * bool(count - 1))
                     for class_name, count in status.total_exited.items()
                     if count > 0])
                if len(exiting_counts):
                    text += f"\n{exiting_text}{exiting_counts}"

            counts = status.detection_within_counts
            if len(counts):
                within_text = QApplication.translate(
                    "ZoneStatusPolygon",
                    "Within: ")
                text += f"\n{within_text}"
                items = list(counts.items())
                items.sort()
                text += "\n" + "\n".join([f"{v} {k}{'s' * bool(v - 1)}"
                                          for k, v in items])
        else:
            # If the zone is a region
            counts = status.detection_within_counts
            items = list(counts.items())
            items.sort()
            text += "\n" + "\n".join([f"{v} {k}{'s' * bool(v - 1)}"
                                      for k, v in items])
        text = text.strip()

        if len(status.alerts):
            alert_text = QApplication.translate("ZoneStatusPolygon", "Alert!")
            text += f"\n{alert_text}"

        # Set opacity based on alert status and detection status
        opacity = 0.3
        if len(status.alerts) or len(status.within) or len(status.entering) \
                or len(status.exiting):
            opacity = 1

        # Set the color based on whether or not there is an ongoing alert
        color = (self.ALERTING_COLOR if len(status.alerts)
                 else self.NORMAL_COLOR)

        # Create the polygon
        super().__init__(points=status.zone.coords,
                         border_color=color,
                         border_thickness=border_thickness,
                         border_linetype=Qt.DotLine,
                         opacity=opacity,
                         parent=parent)

        # Create the label box
        self.label_box = StreamLabelBox(text,
                                        text_size=text_size,
                                        top_left=top_left,
                                        parent=self)
