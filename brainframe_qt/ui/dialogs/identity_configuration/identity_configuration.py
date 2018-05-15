from collections import defaultdict
from pathlib import Path
import re
from typing import Dict, List

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from .directory_selector import DirectorySelector
from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.api import api
from brainframe.client.api.codecs import Identity


# TODO: Use @dataclass decorator in Python3.7
class IdentityPrototype:
    """Prototype for identity codec

    Used before adding to server
    """

    def __init__(self):
        self.identity_id: str = None
        self.nickname: str = None
        self.images: Dict[str, List[bytes]] = defaultdict(list)


class IdentityConfiguration(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # loadUi(qt_ui_paths.identity_configuration_ui, self)

    def create_new_identities(self):

        for identity_prototype in self.get_new_identities_from_path():

            for class_name, images in identity_prototype.images.items():

                identity = Identity(
                    unique_name=identity_prototype.identity_id,
                    nickname=identity_prototype.nickname,
                    metadata="{}",
                    class_name=class_name
                )

                identity = api.set_identity(identity)

                for image in images:
                    api.new_identity_image(identity.id, image)

    @staticmethod
    def get_new_identities_from_path() -> List[IdentityPrototype]:

        path = DirectorySelector().get_path()

        identity_prototypes: List[IdentityPrototype] = []

        # Iterate over identities
        # Identities directories are named using the following format:
        #     identity_id (nickname)/
        for identity_dir in filter(Path.is_dir, path.iterdir()):
            identity_prototype = IdentityPrototype()

            match = re.search(r"(.*?)\s*\((.*)\)$", identity_dir.name)

            # TODO: Warn
            if not match:
                print("Unknown file", identity_dir)
                continue

            identity_prototype.identity_id = match[1]
            identity_prototype.nickname = match[2]

            # Iterate over encoding class types
            for class_dir in identity_dir.iterdir():

                for resource in class_dir.iterdir():
                    with open(resource, "rb") as image:
                        identity_prototype.images[class_dir.name].append(
                            image.read())

            identity_prototypes.append(identity_prototype)

        return identity_prototypes
