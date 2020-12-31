from .all_resource_paths import register_path

# Translation paths
i18n_dir = register_path("brainframe_qt", "ui", "resources", "i18n")
for translation_file in i18n_dir.glob("*.qm"):
    register_path(translation_file)

# License paths
eula_txt = register_path("brainframe_qt", "legal", "eula.txt")
sources_txt = register_path("brainframe_qt", "legal", "sources.txt")
license_dir = register_path("brainframe_qt", "legal", "licenses")
for license_file in license_dir.iterdir():
    register_path(license_file)
