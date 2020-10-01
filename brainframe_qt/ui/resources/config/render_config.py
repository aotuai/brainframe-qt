from brainframe.client.ui.resources.settings import QSettingsConfig, Setting


class RenderSettings:
    # Render Configuration Settings
    draw_lines = Setting(
        True, type_=bool, name="video_draw_lines")
    draw_regions = Setting(
        True, type_=bool, name="video_draw_regions")
    draw_detections = Setting(
        True, type_=bool, name="video_draw_detections")
    use_polygons = Setting(
        True, type_=bool, name="video_use_polygons")
    show_detection_tracks = Setting(
        True, type_=bool, name="video_show_tracks")
    show_recognition_labels = Setting(
        True, type_=bool, name="video_show_confidence")
    show_detection_labels = Setting(
        True, type_=bool, name="video_show_detection_labels")
    show_attributes = Setting(
        True, type_=bool, name="video_show_attributes")
    show_extra_data = Setting(
        False, type_=bool, name="video_show_extra_data")


_render_settings = RenderSettings()


class QSettingsRenderConfig(QSettingsConfig):
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

    def __init__(self):
        super().__init__(_render_settings)
