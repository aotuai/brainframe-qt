from brainframe_qt.ui.resources.settings import Setting, SettingsManager


class LicensingSettings(SettingsManager):
    eula_accepted = Setting(name="client_license_accepted", default=None, type_=str)
    eula_md5 = Setting(name="client_license_md5", default=None, type_=str)
