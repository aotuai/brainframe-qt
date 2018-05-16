from collections import defaultdict
from pathlib import Path
import re
from typing import Dict, List, Set

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from .directory_selector import DirectorySelector
from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.api import api, APIError
from brainframe.client.api.codecs import Identity
from brainframe.shared import rest_errors


# TODO: Use @dataclass decorator in Python3.7
class IdentityPrototype:
    """Prototype for identity codec

    Used before adding to server
    """

    def __init__(self):
        self.unique_name: str = None
        self.nickname: str = None
        self.images: Dict[str, List[bytes]] = defaultdict(list)


class IdentityConfiguration(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # loadUi(qt_ui_paths.identity_configuration_ui, self)

    def create_new_identities(self):

        duplicate_identities: Set[str] = set()
        missing_identities: Set[str] = set()
        unencodable_class_types: Set[str] = set()

        for identity_prototype in self.get_new_identities_from_path():

            for class_name, images in identity_prototype.images.items():

                identity = Identity(
                    unique_name=identity_prototype.unique_name,
                    nickname=identity_prototype.nickname,
                    metadata={})

                try:
                    identity = api.set_identity(identity)
                except APIError as err:
                    if err.kind == rest_errors.DUPLICATE_IDENTITY_NAME:
                        # Identity already exists
                        identity = api.get_identities(
                            unique_name=identity_prototype.unique_name)[0]
                        duplicate_identities.add(identity.unique_name)
                    else:
                        # Re-raise other kinds of APIErrors
                        raise err

                for image in images:
                    try:
                        api.new_identity_image(identity.id, class_name, image)
                    except APIError as err:
                        if err.kind == rest_errors.IDENTITY_NOT_FOUND:
                            missing_identities.add(identity.unique_name)
                        elif err.kind == rest_errors.NOT_ENCODABLE:
                            unencodable_class_types.add(identity.unique_name)
                        else:
                            raise err  # Re-raise other kinds of APIErrors

        # TODO: Popup message
        if duplicate_identities:
            print("The following identities already exist in database:",
                  duplicate_identities)
        if missing_identities:
            print("The following images are missing identities "
                  "(this should never happen):", missing_identities)
        if unencodable_class_types:
            # TODO: The actual class type causing issues
            print("The following images have an unencodable class type:",
                  unencodable_class_types)

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

            identity_prototype.unique_name = match[1]
            identity_prototype.nickname = match[2]

            # Iterate over encoding class types
            for class_dir in identity_dir.iterdir():

                for resource in class_dir.iterdir():
                    with open(resource, "rb") as image:
                        identity_prototype.images[class_dir.name].append(
                            image.read())

            identity_prototypes.append(identity_prototype)

        return identity_prototypes
