import typing
from typing import Any

from brainframe.client.ui.resources import settings


class QSettingsRenderConfig:
    # https://stackoverflow.com/a/58278544/8134178

    draw_lines: bool
    draw_regions: bool
    draw_detections: bool

    use_polygons: bool

    show_recognition_labels: bool

    show_detection_tracks: bool
    show_detection_labels: bool

    show_attributes: bool
    show_extra_data: bool

    def __getattribute__(self, item: str) -> Any:
        if item not in typing.get_type_hints(type(self)):
            return super().__getattribute__(item)

        try:
            return super().__getattribute__(f"_{item}")
        except AttributeError:
            return getattr(settings, item).val()

    def __setattr__(self, key: str, value: Any):
        if key not in typing.get_type_hints(type(self)):
            raise AttributeError(f"Unknown option '{key}'")

        super().__setattr__(f"_{key}", value)
