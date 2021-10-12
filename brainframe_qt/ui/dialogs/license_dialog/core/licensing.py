from brainframe_qt.api_utils import api
from brainframe_qt.util.licensing import LicenseInfo


def get_brainframe_license_info() -> LicenseInfo:
    api_license_info = api.get_license_info()
    return LicenseInfo.from_api_info(api_license_info)

