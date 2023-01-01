from brainframe_qt.ui.resources.settings import Setting, SettingsManager


class RenderSettings(SettingsManager):
    draw_lines = Setting(
        name="video_draw_lines",
        default=True,
        type_=bool,
    )
    draw_regions = Setting(
        name="video_draw_regions",
        default=True,
        type_=bool,
    )
    draw_detections = Setting(
        name="video_draw_detections",
        default=True,
        type_=bool,
    )
    delay_compensation = Setting(name="video_delay_compensation", default=0.0, type_=float)
    use_polygons = Setting(
        name="video_use_polygons",
        default=True,
        type_=bool,
    )
    show_detection_tracks = Setting(
        name="video_show_tracks",
        default=True,
        type_=bool,
    )
    show_recognition_labels = Setting(
        name="video_show_confidence",
        default=True,
        type_=bool,
    )
    show_detection_labels = Setting(
        name="video_show_detection_labels",
        default=True,
        type_=bool,
    )
    show_attributes = Setting(
        name="video_show_attributes",
        default=True,
        type_=bool,
    )
    show_extra_data = Setting(
        name="video_show_extra_data",
        default=False,
        type_=bool,
    )
