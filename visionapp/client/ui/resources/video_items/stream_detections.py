import random

from PyQt5.QtGui import QColor

from visionapp.client.api import codecs
from visionapp.client.ui.resources.video_items import StreamPolygon
from visionapp.client.ui.resources.video_items.stream_polygon import StreamLabelBox


def generate_unique_qcolor(name: str):
    """Generate a unique QColor based on a string name"""
    rand_seed = random.Random(name)
    hue = rand_seed.random()
    return QColor.fromHsvF(hue, 1.0, 1.0)


class DetectionPolygon(StreamPolygon):
    """Render a Detection polygon with a title and behaviour information"""
    MAX_SECONDS_OLD = 3
    """After a certain amount of time, the detection will be transparent"""

    def __init__(self, det: codecs.Detection, seconds_old=0, parent=None):
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
        text = det.class_name + "\n" + "".join([a.category + ": " + a.value
                                                for a in det.attributes])
        self.label_box = StreamLabelBox(text,
                                        top_left=top_left,
                                        parent=self)


class ZoneStatusPolygon(StreamPolygon):
    """Render a ZoneStatus's Zone along with information about the Zone
    Status"""

    def __init__(self, status: codecs.ZoneStatus, parent=None):
        color = generate_unique_qcolor(status.zone.name)

        super().__init__(points=status.zone.coords,
                         border_color=color,
                         border_thickness=2,
                         parent=parent)

        # Find the top-left point of the zone
        top_left = sorted(self.points_list,
                          key=lambda pt: pt[0] ** 2 + pt[1] ** 2)[0]

        # Create the description box for the zone
        text = status.zone.name + "\nEntered: "
        text += ", ".join([str(v) + " " + k + "s"
                           for k, v in status.total_entered.items()])
        text += "\nExited: "
        text += ", ".join([str(v) + " " + k + "s"
                           for k, v in status.total_exited.items()])

        if len(status.alerts):
            text += "\nAlert!!!"
        self.label_box = StreamLabelBox(text,
                                        top_left=top_left,
                                        parent=self)
