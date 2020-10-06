import glob
import importlib.util
import os
from pathlib import Path

import sys

from brainframe.client.ui.resources.paths import route_path


class ExtensionLoader:
    extension_namespace = "bfc_extensions"

    @property
    def extension_dir(self) -> Path:

        root_dir = Path(sys.modules['__main__'].__file__).parent

        return Path(os.environ.get("EXTENSION_LIB", root_dir / "extensions"))

    def load_extensions(self):

        if not self.extension_dir.is_dir():
            return

        extension_dir = route_path(self.extension_dir)
        extension_pattern = str(extension_dir / "**" / "extension.py")
        # Can't use Path.glob: https://bugs.python.org/issue33428
        for extension_init in map(Path, glob.glob(extension_pattern)):
            extension_dir = extension_init.parent
            self._load_extension(extension_dir)

    def _load_extension(self, extension_path: Path):

        # Load module
        extension_name = extension_path.name
        extension_module_name = f"{self.extension_namespace}.{extension_name}"

        package_spec = importlib.util.spec_from_file_location(
            name=extension_module_name,
            location=extension_path / "__init__.py"
        )
        package_module = importlib.util.module_from_spec(package_spec)
        package_spec.loader.exec_module(package_module)

        # Register the module. Don't overwrite existing modules
        if extension_module_name in sys.modules:
            raise self.DuplicateModuleNameError(extension_module_name)

        sys.modules[extension_module_name] = package_module

        extension_spec = importlib.util.spec_from_file_location(
            name=f"{extension_module_name}.extension",
            location=extension_path / "extension.py"
        )
        extension_module = importlib.util.module_from_spec(extension_spec)
        extension_spec.loader.exec_module(extension_module)

        # Register the extension. Don't overwrite existing modules
        sys.modules[f"{extension_module_name}.extension"] = extension_module

    class DuplicateModuleNameError(ImportError):
        def __init__(self, module_name: str):
            message = f"Extension with name {module_name} already exists. " \
                      f"Unable to load extension with the same name."
            super().__init__(message, name=module_name)
