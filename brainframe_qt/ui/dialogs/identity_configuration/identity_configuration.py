from collections import defaultdict
from pathlib import Path
import re
from typing import Dict, List, Set, Tuple, Union

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QObject, QThread
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QMessageBox
from PyQt5.uic import loadUi

from .directory_selector import DirectorySelector
from .identity_error_popup import IdentityError, IdentityErrorPopup
from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.api import api, api_errors
from brainframe.client.api.codecs import Identity


# TODO: Use @dataclass decorator in Python3.7
class IdentityPrototype:
    """Prototype for identity codec

    Used before adding to server
    """

    def __init__(self):
        self.unique_name: str = None
        self.nickname: str = None
        self.images: Dict[str, List[Tuple[Path, bytes]]] = defaultdict(list)


class IdentityConfiguration(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_configuration_ui, self)

        self.progress_bar.setHidden(True)

        # Create thread to send images
        self.worker = ImageSenderWorker()
        self.thread = QThread(self)
        self.thread.setObjectName("ImageSenderWorkerThread")
        self.worker.moveToThread(self.thread)
        # noinspection PyUnresolvedReferences
        self.worker.update_progress_bar.connect(self.update_progress_bar)

        # noinspection PyUnresolvedReferences
        self.thread.started.connect(
            lambda: self.worker.send_images(self.identity_prototypes))
        # noinspection PyUnresolvedReferences
        self.worker.done_sending.connect(self.images_done_sending)
        # noinspection PyUnresolvedReferences
        self.worker.update_tree_view.connect(self.update_tree_view)

        self.add_identities_button.clicked.connect(self.create_new_identities)

        self.add_db_identities_to_tree()

        self.identity_prototypes = None

    @classmethod
    def show_dialog(cls):

        dialog = cls()
        dialog.exec_()

    def create_new_identities(self):

        # Get a all identities to add to server and the number of images.
        # Change the function called here to be different method of adding
        # identities if desired
        self.identity_prototypes, num_images = \
            self.get_new_identities_from_path()

        # User canceled
        if self.identity_prototypes is None:
            return

        self.thread.start()

        # Set max value for progress bar
        self.progress_bar.setHidden(False)
        self.progress_bar.setMaximum(num_images)

    @pyqtSlot(str, str, str)
    def update_tree_view(self, unique_name, class_name, image_name):

        identity_tree_item = self.identity_tree.findItems(
            unique_name,
            Qt.MatchExactly)

        if not identity_tree_item:
            QTreeWidgetItem(self.identity_tree, [unique_name])

            # TODO: This line resolves BF-220.
            # It might be a hack instead of a fix
            self.repaint()

        # TODO: Encodings and images

    @pyqtSlot(int)
    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    @pyqtSlot()
    def images_done_sending(self):
        self.thread.quit()
        self.progress_bar.setHidden(True)

    def add_db_identities_to_tree(self):

        identities = api.get_identities()

        for identity in identities:
            QTreeWidgetItem(self.identity_tree, [identity.unique_name])

    @classmethod
    def get_new_identities_from_path(cls) \
            -> Tuple[Union[None, List[IdentityPrototype]], int]:
        """Get a list of IdentityPrototypes for sending to server, and the total
        number of images

        :returns Tuple[List[IdentityPrototype], int]
        """
        path = DirectorySelector().get_path()

        # User canceled
        if path is None:
            return None, 0

        # TODO: Error is excessively vague. Should be within the function
        try:
            num_images = cls.verify_directory_structure(path)
        except ValueError as err:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Invalid Format")

            # TODO: Use fstrings
            error_dialog.setText(f"Unable to parse this directory!\n\n"
                                 f"Reason:\n"
                                 f"{err}\n\n"
                                 f"Read the manual to learn about the required " 
                                 f"directory structure.")
            print("Error")
            error_dialog.exec_()
            return None, 0

        identity_prototypes: List[IdentityPrototype] = []

        # Iterate over identities
        # Identities directories are named using the following format:
        #     identity_id (nickname)/
        for identity_dir in path.iterdir():
            identity_prototype = IdentityPrototype()

            # TODO: Better regex to avoid if-else
            if '(' not in identity_dir.name:
                identity_prototype.unique_name = identity_dir.name
                identity_prototype.nickname = None
            else:
                match = re.search(r"(.+?)\s*\((.*)\)", identity_dir.name)

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

        return identity_prototypes, num_images

    @staticmethod
    def verify_directory_structure(path: Path) -> int:
        """Verify that the directory is structured properly

        :return int: Number of images in directory, for progress indication
        """
        num_images = 0

        if not path.is_dir():
            raise ValueError(f"Path {path} is not a directory.")

        if not path.iterdir():
            raise ValueError(f"Path {path} has no children")

        for identity_dir in path.iterdir():

            if not identity_dir.is_dir():
                raise ValueError(f"Identity {identity_dir} is not a directory.")

            for encoding_dir in identity_dir.iterdir():

                if not encoding_dir.is_dir():
                    raise ValueError(f"Class {encoding_dir} is not a "
                                     f"directory.")

                for image in encoding_dir.iterdir():

                    if not image.is_file():
                        raise ValueError(f"Image {image} is not a file.")

                    num_images += 1

        return num_images


class ImageSenderWorker(QObject):
    update_tree_view = pyqtSignal(str, str, str)
    update_progress_bar = pyqtSignal(int)
    done_sending = pyqtSignal()

    @pyqtSlot(object)
    def send_images(self, identity_prototypes):

        errors: Set[IdentityError] = set()

        processed_images = 0
        for identity_prototype in identity_prototypes:

            identity = Identity(
                unique_name=identity_prototype.unique_name,
                nickname=identity_prototype.nickname,
                metadata={})

            identity_error = IdentityError(identity.unique_name)

            try:
                identity = api.set_identity(identity)
            except api_errors.DuplicateIdentityNameError:
                # Identity already exists
                identity = api.get_identities(
                    unique_name=identity_prototype.unique_name
                )[0]

                # This error is a warning. Don't show it to user
                pass
            except api_errors.BaseAPIError as err:
                identity_error.error = err.kind

            for class_name, images in identity_prototype.images.items():

                # Create an error object for the class so it can be used if
                # necessary
                class_name_error = IdentityError(class_name)

                for image_name, image_bytes in images:

                    try:
                        image_id = api.new_storage_as_image(image_bytes)
                        api.new_identity_image(
                            identity.id,
                            class_name,
                            image_id)

                        # Update UI's tree view if successful
                        # noinspection PyUnresolvedReferences
                        self.update_tree_view.emit(
                            identity.unique_name,
                            class_name,
                            image_name.name)

                    except (api_errors.NoEncoderForClassError,
                            api_errors.NoDetectorForClassError) as err:
                        class_name_error.error = err.kind
                    except api_errors.ImageAlreadyEncodedError:
                        pass
                    except api_errors.BaseAPIError as err:
                        image_error = IdentityError(image_name.name, str(err))
                        class_name_error.children.add(image_error)

                    processed_images += 1
                    # noinspection PyUnresolvedReferences
                    self.update_progress_bar.emit(processed_images)

                # If the current class has an error or children, add it to the
                # identity's set of errors
                if class_name_error.error or class_name_error.children:
                    identity_error.children.add(class_name_error)

            # If the current identity has an error or children, add it to the
            # set of errors
            if identity_error.error or identity_error.children:
                errors.add(identity_error)

        # noinspection PyUnresolvedReferences
        self.done_sending.emit()

        # If there are errors, show them to the user
        if errors:
            IdentityErrorPopup.show_errors(errors)
