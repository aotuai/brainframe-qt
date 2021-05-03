import pendulum
from brainframe_qt.ui.resources.settings import Setting, SettingsManager
from pendulum.tz.zoneinfo import Timezone


class LocaleSettings(SettingsManager):
    user_timezone = Setting(
        name="user_timezone",
        default="",
        type_=str,
    )

    def get_user_timezone(self) -> Timezone:
        if self.user_timezone == "":
            return pendulum.now().timezone
        else:
            return pendulum.timezone(self.user_timezone)
