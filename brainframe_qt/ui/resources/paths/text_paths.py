from .all_resource_paths import register_path

# Translation paths
i18n_dir = register_path("brainframe", "client", "ui", "resources", "i18n")
for translation_file in i18n_dir.glob("*.qm"):
    register_path(translation_file)

# License paths
eula_txt = register_path("licenses", "eula.txt")
license_dir = register_path("brainframe", "client", "licenses")
for license_file in license_dir.iterdir():
    register_path(license_file)
