from visionapp.client.ui.resources import BasePlugin


class VideoTaskConfig(BasePlugin):

    # noinspection PyUnresolvedReferences
    from visionapp.client.ui.dialogs.task_configuration.video_task_config. \
        video_task_config import VideoTaskConfig as Widget

    def __init__(self):

        super().__init__(self.Widget)
