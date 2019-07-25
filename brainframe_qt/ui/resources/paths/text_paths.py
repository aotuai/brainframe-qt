from .all_resource_paths import route_path

# Translation paths
i18n_dir = route_path("brainframe") / "client" / "ui" / "resources" / "i18n"

# License paths
license_agreement_txt = route_path("license.txt")
license_dir = route_path("brainframe", "shared", "licenses")
for license_file in license_dir.iterdir():
    route_path(license_file)
