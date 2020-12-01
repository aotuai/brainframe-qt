from typing import List, Optional, Tuple

from PyQt5.QtGui import QColor
from brainframe.api.bf_codecs import Detection

from brainframe_qt.ui.resources.config import QSettingsRenderConfig
from brainframe_qt.ui.resources.video_items.base import LabelItem, \
    VideoItem


class DetectionLabelItem(LabelItem):
    MIN_WIDTH = 150

    def __init__(self, detection: Detection, color: QColor,
                 *, render_config: QSettingsRenderConfig, parent: VideoItem):

        self.detection = detection
        self.render_config = render_config

        super().__init__(self.text, self._detection_pos,
                         color=color, max_width=self._max_label_width,
                         parent=parent)

        # TODO: background opacity

    @property
    def _detection_pos(self) -> Tuple[int, int]:
        # Naive. Maybe refine for non-rectangular detections in future?
        top_left = self.detection.coords[0]

        # noinspection PyTypeChecker
        return tuple(top_left)

    @property
    def text(self):
        text_items = []

        if self.render_config.show_detection_labels:
            text_items.append(self._detection_name_text)
        if self.render_config.show_recognition_labels:
            text_items.append(self._recognition_text)
        if self.render_config.show_attributes:
            text_items.append(self._attributes_text)
        if self.render_config.show_extra_data:
            text_items.append(self._extra_data_text)

        text = "\n".join(filter(None.__ne__, text_items))
        return text

    @property
    def _detection_name_text(self):
        return self.detection.class_name

    @property
    def _recognition_text(self) -> Optional[str]:
        identity = self.detection.with_identity

        if identity is None:
            return None

        nickname = identity.nickname
        unique_name = identity.unique_name
        name = unique_name if nickname is None else nickname

        confidence = self.detection.extra_data['encoding_distance']

        return f"{name} ({round(confidence, 2)}"

    @property
    def _attributes_text(self) -> Optional[str]:
        attributes = self.detection.attributes

        attribute_strings = sorted(f"{key}: {val}"
                                   for key, val in attributes.items())

        attribute_text = "\n".join(attribute_strings)

        return attribute_text or None

    @property
    def _extra_data_text(self) -> Optional[str]:
        extra_data = self.detection.extra_data

        extra_data_strings: List[str] = []
        for key, val in extra_data.items():
            if isinstance(val, float):
                val = round(val, 3)
            extra_data_strings.append(f"{key}: {val}")

        extra_data_text = "\n".join(extra_data_strings)

        return extra_data_text or None

    @property
    def _max_label_width(self) -> int:
        # Naive. Maybe refine for non-rectangular detections in future?
        detection_width = self.detection.bbox[1][0] - self.detection.bbox[0][0]

        return max(self.MIN_WIDTH, detection_width)
