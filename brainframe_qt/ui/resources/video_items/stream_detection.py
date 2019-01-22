import random

from PyQt5.QtGui import QColor

from brainframe.client.api.streaming import DetectionTrack
from brainframe.client.api.codecs import Detection
from brainframe.client.ui.resources.video_items import (
    StreamLabelBox,
    StreamPolygon
)


def generate_unique_qcolor(name: str):
    """Generate a unique QColor based on a string name"""
    rand_seed = random.Random(name)
    hue = rand_seed.random()
    return QColor.fromHsvF(hue, 1.0, 1.0)


class DetectionPolygon(StreamPolygon):
    """Render a Detection polygon with a title and behaviour information"""

    MAX_TRACK_AGE = 10
    """Remove tracks over X seconds long"""

    def __init__(self,
                 detection: Detection,
                 track: DetectionTrack,
                 text_size,
                 *,
                 use_polygons=True,
                 show_detection_labels=True,
                 show_attributes=True,
                 parent=None):
        """
        :param detection: The Detection object to render
        :param seconds_old: Fades the detection by a standard amount based on
        it's age.
        :param parent:
        """
        # Choose a color for this class name
        class_color = generate_unique_qcolor(detection.class_name)

        super().__init__(detection.coords,
                         border_color=class_color,
                         border_thickness=1,
                         parent=parent)

        # Create the description box
        top_left = detection.coords[0]
        text = detection.class_name

        # Add "Identity" to the description box
        if detection.with_identity is not None:
            if detection.with_identity.nickname is not None:
                text += "\n" + "Name: " + detection.with_identity.nickname
            else:
                text += "\n" + "Name: " + detection.with_identity.unique_name

        if len(detection.attributes):
            attributes_str_list = [a.category + ": " + a.value
                                   for a in detection.attributes]
            attributes_str_list.sort()
            text += "\n" + "\n".join(attributes_str_list)

        self.label_box = StreamLabelBox(text,
                                        top_left=top_left,
                                        text_size=text_size,
                                        parent=self)

        self.line_item = None
        if len(track) > 1:
            # Draw a track for the detections history
            line_coords = []
            for prev_det, detection_tstamp in track:
                # Find the point of the detection closest to the screens bottom
                if track.latest_tstamp - detection_tstamp > self.MAX_TRACK_AGE:
                    break
                line_coords.append(prev_det.center)

                # TODO: Find the bottom of the polygon, and draw the line there
                # draw lines from there.
                # poly = LineString(prev_det.coords)
                # screen_bottom = Point([prev_det.center[0], 10000])
                # nearest_point = list(poly.interpolate(
                #     poly.project(screen_bottom)).coords)
                # line_coords.append(nearest_point)
            self.line_item = StreamPolygon(
                points=line_coords,
                border_color=class_color,
                close_polygon=False,
                opacity=.5,
                parent=self)
