from brainframe_qt.ui.resources.settings import Setting, SettingsManager


class StreamingSettings(SettingsManager):
    frame_buffer_size = Setting(name="frame_buffer_size", default=300, type_=int)
