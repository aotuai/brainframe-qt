from brainframe_qt.ui.resources.settings import QSettingsConfig, Setting


class ServerSettings:
    # Server Configuration Settings
    server_url = Setting("http://localhost", type_=str, name="server_url")
    server_username = Setting(None, type_=str, name="server_username")
    server_password = Setting(None, type_=bytes, name="server_password")


_server_settings = ServerSettings()


class QSettingsServerConfig(QSettingsConfig):
    # https://stackoverflow.com/a/58278544/8134178

    server_url: str
    server_username: str
    server_password: bytes

    def __init__(self):
        super().__init__(_server_settings)
