import random

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from visionapp.client.api import codecs
from visionapp.client.ui.resources.video_items import StreamPolygon
from visionapp.client.ui.resources.video_items.stream_polygon import \
    StreamLabelBox


def generate_unique_qcolor(name: str):
    """Generate a unique QColor based on a string name"""
    rand_seed = random.Random(name)
    hue = rand_seed.random()
    return QColor.fromHsvF(hue, 1.0, 1.0)


class DetectionPolygon(StreamPolygon):
    """Render a Detection polygon with a title and behaviour information"""
    MAX_SECONDS_OLD = 1.5
    """After a certain amount of time, the detection will be transparent"""

    def __init__(self, det: codecs.Detection, attributes=set(), seconds_old=0,
                 parent=None):
        """
        :param detection: The Detection object to render
        :param seconds_old: Fades the detection by a standard amount based on
        it's age.
        :param parent:
        """
        # Choose a color for this class name
        class_color = generate_unique_qcolor(det.class_name)

        # Choose the opacity based on the age of the detection
        clamped_age = sorted([0, seconds_old, self.MAX_SECONDS_OLD])[1]
        opacity = 1 - clamped_age / self.MAX_SECONDS_OLD
        opacity += 0.05  # Minimum opacity for a detection

        super().__init__(det.coords,
                         border_color=class_color,
                         border_thickness=1,
                         opacity=opacity, parent=parent)

        # Create the description box
        top_left = det.coords[0]
        text = det.class_name
        if len(attributes):
            attributes_str_list = [a.category + ": " + a.value
                                   for a in det.attributes if
                                   a.value in attributes]
            attributes_str_list.sort()
            text += "\n" + "\n".join(attributes_str_list)

        self.label_box = StreamLabelBox(text,
                                        top_left=top_left,
                                        parent=self)


class ZoneStatusPolygon(StreamPolygon):
    """Render a ZoneStatus's Zone along with information about the Zone
    Status"""
    NORMAL_COLOR = QColor(0, 255, 125)
    ALERTING_COLOR = QColor(255, 125, 0)

    def __init__(self, status: codecs.ZoneStatus, *,
                 border_thickness=1, parent=None):

        # Find the top-left point of the zone
        top_left = sorted(status.zone.coords,
                          key=lambda pt: pt[0] ** 2 + pt[1] ** 2)[0]

        # Create the description box for the zone
        text = status.zone.name
        if len(status.zone.coords) == 2:
            # If the zone is a line
            text = status.zone.name + "\nCrossed: "
            text += ", ".join(["{} {}{}".format(v, k, "s" * bool(v - 1))
                               for k, v in status.total_exited.items()
                               if v > 0])
        else:
            # If the zone is a region
            counts = status.detection_counts
            text += "\n" + "\n".join(["{} {}{}".format(v, k, "s" * bool(v - 1))
                                      for k, v in counts.items()])
        text = text.strip()

        if len(status.alerts):
            text += "\nAlert!"

        # Set opacity based on alert status and detection status
        opacity = 0.3
        if len(status.alerts) or len(status.detections):
            opacity = 1

        # Set the color based on whether or not there is an ongoing alert
        color = self.ALERTING_COLOR if len(status.alerts) else self.NORMAL_COLOR

        # Create the polygon
        super().__init__(points=status.zone.coords,
                         border_color=color,
                         border_thickness=border_thickness,
                         border_linetype=Qt.DotLine,
                         opacity=opacity,
                         parent=parent)

        # Create the label box
        self.label_box = StreamLabelBox(text,
                                        top_left=top_left,
                                        parent=self)
