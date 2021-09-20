from dataclasses import dataclass

from brainframe_qt.util.licensing import LicenseInfo


@dataclass
class LicensedProduct:
    name: str
    icon_resource: str  # Qt resource path, not file path
    license_info: LicenseInfo
