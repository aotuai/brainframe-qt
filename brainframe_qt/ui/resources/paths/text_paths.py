from .all_resource_paths import register_path

# Translation paths
i18n_dir = register_path("brainframe", "client", "ui", "resources", "i18n")
for translation_file in i18n_dir.glob("*.qm"):
    register_path(translation_file)

# License paths
license_agreement_txt = register_path("license.txt")
license_dir = register_path("brainframe", "shared", "licenses")
for license_file in license_dir.iterdir():
    register_path(license_file)
