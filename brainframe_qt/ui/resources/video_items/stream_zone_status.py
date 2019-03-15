from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from brainframe.client.api import codecs
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
            text = status.zone.name + "\nEntering: "
            text += ", ".join(["{} {}{}".format(v, k, "s" * bool(v - 1))
                               for k, v in status.total_entered.items()
                               if v > 0])
            text += "\nExiting: "
            text += ", ".join(["{} {}{}".format(v, k, "s" * bool(v - 1))
                               for k, v in status.total_exited.items()
                               if v > 0])
        else:
            # If the zone is a region
            counts = status.detection_within_counts
            items = list(counts.items())
            items.sort()
            text += "\n" + "\n".join([f"{v} {k}{'s' * bool(v - 1)}"
                                      for k, v in items])
        text = text.strip()

        if len(status.alerts):
            text += "\nAlert!"

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
