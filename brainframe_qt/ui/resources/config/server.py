from brainframe_qt.ui.resources.settings import Setting, SettingsManager


class ServerSettings(SettingsManager):
    server_url = Setting(name="server_url", default="http://localhost", type_=str)
    server_username = Setting(name="server_username", default=None, type_=str)
    server_password = Setting(name="server_password", default=None, type_=bytes)
