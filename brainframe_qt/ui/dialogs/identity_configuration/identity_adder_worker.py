from pathlib import Path
from typing import List, Set

import typing
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QWidget

from brainframe.client.api import api
from brainframe.api import api_errors
from brainframe.api.codecs import Identity
from brainframe.client.api.identities import FileTreeIdentityFinder
from brainframe.client.api.identities import IdentityPrototype

from .directory_selector import DirectorySelector
from .identity_error_popup import IdentityError, IdentityErrorPopup


class AddNewIdentitiesWorker(QThread):
    identity_uploaded_signal = pyqtSignal(object)
    """Emitted whenever a new identity is uploaded to the database"""
    identity_upload_progress_signal = pyqtSignal(int, int)
    """Emits number of identities that have been uploaded so far."""

    def __init__(self, parent: QObject = None):
        super().__init__(parent=parent)

        self.identity_prototypes: List[IdentityPrototype] = []
        self.num_images: int = -1

        self.setObjectName("IdentityUploadWorkerThread")

        self.errors: Set[IdentityError] = set()
        self.finished.connect(self.show_errors)

    def add_identities_from_file(self):

        path = DirectorySelector.get_path(self.parent())

        # User canceled
        if path is None:
            return

        if not path.is_file():
            self._handle_missing_dir_error(path)
            return

        # TODO: Error is excessively vague. Should be within the function
        try:
            identity_finder = FileTreeIdentityFinder(path)
            self.num_images = identity_finder.num_encodings
        except ValueError as err:

            message = self.tr("Unable to parse this directory!\n\n"
                              "Reason:\n"
                              "{}\n\n"
                              "Read the manual to learn about the required "
                              "directory structure.").format(err)

            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle(self.tr("Invalid Format"))
            error_dialog.setText(message)
            error_dialog.exec_()
            return

        self.identity_prototypes = identity_finder.find()

        self.start()

    def show_errors(self):
        # If there are errors, show them to the user
        if self.errors:
            IdentityErrorPopup.show_errors(self.errors, self.parent())
            self.errors = set()

    def run(self):

        processed_encodings = 0
        while self.identity_prototypes:
            prototype = self.identity_prototypes.pop()

            identity = Identity(
                unique_name=prototype.unique_name,
                nickname=prototype.nickname,
                metadata={})

            identity_error = IdentityError(identity.unique_name)

            try:
                identity = api.set_identity(identity)
            except api_errors.DuplicateIdentityNameError:
                # Identity already exists
                identities, _ = api.get_identities(
                    unique_name=prototype.unique_name
                )
                identity = identities[0]

                # This error is a warning. Don't show it to user
                pass
            except api_errors.BaseAPIError as err:
                identity_error.error = err.kind

            # Associate images with the identity
            for class_name, images in prototype.images_by_class_name.items():
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

                    except (api_errors.NoEncoderForClassError,
                            api_errors.NoDetectorForClassError) as err:
                        class_name_error.error = err.kind
                    except api_errors.ImageAlreadyEncodedError:
                        pass
                    except api_errors.BaseAPIError as err:
                        image_error = IdentityError(image_name.name,
                                                    err.pretty_name)
                        class_name_error.children.add(image_error)

                    processed_encodings += 1
                    # noinspection PyUnresolvedReferences
                    self.identity_upload_progress_signal.emit(
                        processed_encodings, self.num_images)

                # If the current class has an error or children, add it to the
                # identity's set of errors
                if class_name_error.error or class_name_error.children:
                    identity_error.children.add(class_name_error)

            # Associate vectors with the identity
            for class_name, vectors in prototype.vectors_by_class_name.items():
                # Create an error object for the class so it can be used if
                # necessary
                class_name_error = IdentityError(class_name)

                for file_name, vector in vectors:
                    try:
                        api.new_identity_vector(identity.id,
                                                class_name,
                                                vector)

                    except api_errors.NoEncoderForClassError as err:
                        class_name_error.error = err.kind
                    except api_errors.DuplicateVectorError:
                        pass
                    except api_errors.BaseAPIError as err:
                        image_error = IdentityError(file_name.name,
                                                    err.pretty_name)
                        class_name_error.children.add(image_error)

                processed_encodings += 1
                # noinspection PyUnresolvedReferences
                self.identity_upload_progress_signal.emit(processed_encodings,
                                                          self.num_images)

            # If the current identity has an error or children, add it to the
            # set of errors
            if identity_error.error or identity_error.children:
                self.errors.add(identity_error)

            # noinspection PyUnresolvedReferences
            self.identity_uploaded_signal.emit(identity)

    def _handle_missing_dir_error(self, filepath: Path):
        message_title = self.tr("Invalid directory")
        message_desc = self.tr(f"Directory does not exist or is a file:")
        message = f"{message_desc}<br>" \
                  f"{filepath}"

        parent = typing.cast(QWidget, self.parent())
        QMessageBox.information(parent, message_title, message)
