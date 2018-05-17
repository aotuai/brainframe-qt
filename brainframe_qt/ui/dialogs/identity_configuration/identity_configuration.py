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

        errors = defaultdict(set)

        # Change the function called here to be different method of adding
        # identities if desired
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
                        errors[err.kind].add(identity.unique_name)
                    else:
                        # Re-raise other kinds of APIErrors
                        raise err

                for image in images:
                    try:
                        api.new_identity_image(identity.id, class_name, image)
                    except APIError as err:
                        errors[err.kind].add(identity.unique_name)

        # More detailed errors
        for error, identities in errors.items():
            print(f"Error `{error}` with the following identities:\n"
                  f"    {identities}")

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
