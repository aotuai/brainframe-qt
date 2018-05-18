from collections import defaultdict
from pathlib import Path
import re
from typing import Dict, List, Set, Tuple

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from .directory_selector import DirectorySelector
from .identity_error_popup import IdentityError, IdentityErrorPopup
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
        self.images: Dict[str, List[Tuple[Path, bytes]]] = defaultdict(list)


class IdentityConfiguration(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # loadUi(qt_ui_paths.identity_configuration_ui, self)

    def create_new_identities(self):

        errors: Set[IdentityError] = set()

        # Change the function called here to be different method of adding
        # identities if desired
        for identity_prototype in self.get_new_identities_from_path():

            identity = Identity(
                unique_name=identity_prototype.unique_name,
                nickname=identity_prototype.nickname,
                metadata={})

            identity_error = IdentityError(identity.unique_name)

            try:
                identity = api.set_identity(identity)
            except APIError as err:
                if err.kind == rest_errors.DUPLICATE_IDENTITY_NAME:
                    # Identity already exists
                    identity = api.get_identities(
                        unique_name=identity_prototype.unique_name
                    )[0]

                    # This error is a warning. Don't show it to user
                    pass

                else:
                    identity_error.error = err.kind

            for class_name, images in identity_prototype.images.items():

                # Create an error object for the class so it can be used if
                # necessary
                class_name_error = IdentityError(class_name)

                for image_name, image_bytes in images:
                    try:
                        api.new_identity_image(
                            identity.id,
                            class_name,
                            image_bytes)
                    except APIError as err:
                        # We don't care about right the error/warning right now
                        if err.kind == rest_errors.NOT_ENCODABLE \
                                or err.kind == rest_errors.NOT_DETECTABLE:
                            class_name_error.error = err.kind
                        if err.kind != rest_errors.IMAGE_ALREADY_ENCODED:
                            image_error = IdentityError(
                                image_name.name,
                                err.kind)
                            class_name_error.children.add(image_error)

                # If the current class has an error or children, add it to the
                # identity's set of errors
                if class_name_error.error or class_name_error.children:
                    identity_error.children.add(class_name_error)

            # If the current identity has an error or children, add it to the
            # set of errors
            if identity_error.error or identity_error.children:
                errors.add(identity_error)

        # If there are errors, show them to the user
        if errors:
            IdentityErrorPopup.show_errors(errors)

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

                for image_name in class_dir.iterdir():
                    with open(image_name, "rb") as image:
                        identity_prototype.images[class_dir.name].append((
                            image_name, image.read()))

            identity_prototypes.append(identity_prototype)

        return identity_prototypes
