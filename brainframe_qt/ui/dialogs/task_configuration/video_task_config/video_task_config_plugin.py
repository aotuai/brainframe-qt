from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class VideoTaskConfig(BasePlugin):

    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.dialogs.task_configuration.video_task_config. \
        video_task_config import VideoTaskConfig as Widget

    def __init__(self):

        super().__init__(self.Widget)
