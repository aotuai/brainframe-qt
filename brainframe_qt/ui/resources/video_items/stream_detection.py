import random

from PyQt5.QtGui import QColor

from brainframe.client.api.streaming import DetectionTrack
from brainframe.client.api.codecs import Detection
from brainframe.client.ui.resources.video_items import (
    StreamLabelBox,
    StreamPolygon
)

_qcolor_cache = {}


def generate_unique_qcolor(seed: str):
    """Generate a unique QColor based on a string seed"""
    if seed not in _qcolor_cache:
        rand_seed = random.Random(seed)
        hue = rand_seed.random()
        _qcolor_cache[seed] = QColor.fromHsvF(hue, 1.0, 1.0)

    return _qcolor_cache[seed]


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
                 show_tracks=True,
                 show_confidence=True,
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

        # Get the polygon to draw
        coords = detection.coords if use_polygons else detection.bbox
        super().__init__(coords,
                         border_color=class_color,
                         border_thickness=1,
                         parent=parent)

        text = ""

        if show_detection_labels:
            text += detection.class_name

        # Add "Identity" to the description box
        if detection.with_identity is not None:
            if detection.with_identity.nickname is not None:
                text += "\nName: " + detection.with_identity.nickname
            else:
                text += "\nName: " + detection.with_identity.unique_name

            if show_confidence:
                confidence = detection.extra_data['encoding_distance']
                text += f" ({round(confidence, 2)})"

        if len(detection.attributes) and show_attributes:
            attributes_str_list = [a.category + ": " + a.value
                                   for a in detection.attributes]
            attributes_str_list.sort()
            text += "\n" + "\n".join(attributes_str_list)

        # Remove all dual newlines
        text = text.strip()
        if len(text):
            # Create the description box
            top_left = coords[0]
            self.label_box = StreamLabelBox(
                title_text=text,
                top_left=top_left,
                text_size=text_size,
                parent=self)

        if len(track) > 1 and show_tracks:
            # Draw a track for the detections history
            line_coords = []
            for prev_det, detection_tstamp in track:
                # Find the point of the detection closest to the screens bottom
                if track.latest_tstamp - detection_tstamp > self.MAX_TRACK_AGE:
                    break
                coord_a, coord_b = sorted(prev_det.coords,
                                          key=lambda pt: -pt[1])[:2]

                # The midpoint will be the next point in our line
                midpoint = [(coord_a[0] + coord_b[0]) / 2,
                            (coord_a[1] + coord_b[1]) / 2]
                line_coords.append(midpoint)

            self.line_item = StreamPolygon(
                points=line_coords,
                border_color=class_color,
                close_polygon=False,
                opacity=.5,
                parent=self)
