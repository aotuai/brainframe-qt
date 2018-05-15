from pathlib import Path
import re

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from .directory_selector import DirectorySelector
from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.api import api
from brainframe.client.api.codecs import Identity


class IdentityConfiguration(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # loadUi(qt_ui_paths.identity_configuration_ui, self)

    def get_new_identities(self):

        path = DirectorySelector().get_path()

        for identity_dir in filter(Path.is_dir, path.iterdir()):
            print(identity_dir.name)

            match = re.search(r"(.*?)\s*\((.*)\)$", identity_dir.name)

            if not match:
                # TODO: Warn
                print("Unknown file", identity_dir)
                continue

            identity_id, nickname = match[1], match[2]

            for class_dir in identity_dir.iterdir():
                print(class_dir.name)

                identity = Identity(identity_id=identity_id,
                                    nickname=nickname,
                                    class_name=class_dir.name)

                identity = api.set_identity(identity)

                for resource in class_dir.iterdir():
                    with open(resource, "rb") as image:
                        image_id = api.new_identity_image(
                            identity.id,
                            image.read())

                        print("Image ID:", image_id)
