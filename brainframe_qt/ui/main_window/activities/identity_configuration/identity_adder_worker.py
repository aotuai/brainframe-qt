import typing
from pathlib import Path
from typing import List, Set

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget
from brainframe.api import bf_codecs, bf_errors

from brainframe.client.api_utils import api
from brainframe.client.api_utils.identities import FileTreeIdentityFinder, \
    IdentityPrototype
from brainframe.client.ui.resources.ui_elements.widgets.dialogs import \
    BrainFrameMessage
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

        if not path.is_dir():
            self._handle_missing_dir_error(path)
            return

        # TODO: Error is excessively vague. Should be within the function
        try:
            identity_finder = FileTreeIdentityFinder(path)
        except ValueError as exc:

            title = self.tr("Invalid directory format")
            message = self.tr("Unable to parse this directory!\n\n"
                              "Read the manual to learn about the required "
                              "directory structure.<br><br>"
                              "{exc}").format(exc=exc)

            BrainFrameMessage.warning(
                parent=typing.cast(QWidget, self.parent()),
                title=title,
                warning=message,
            ).exec()

        else:
            self.num_images = identity_finder.num_encodings
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

            identity = bf_codecs.Identity(
                unique_name=prototype.unique_name,
                nickname=prototype.nickname,
                metadata={})

            identity_error = IdentityError(identity.unique_name)

            try:
                identity = api.set_identity(identity)
            except bf_errors.DuplicateIdentityNameError:
                # Identity already exists
                identities, _ = api.get_identities(
                    unique_name=prototype.unique_name
                )
                identity = identities[0]

                # This error is a warning. Don't show it to user
                pass
            except bf_errors.BaseAPIError as err:
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

                    except (bf_errors.NoEncoderForClassError,
                            bf_errors.NoDetectorForClassError) as err:
                        class_name_error.error = err.kind
                    except bf_errors.ImageAlreadyEncodedError:
                        pass
                    except bf_errors.BaseAPIError as err:
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

                    except bf_errors.NoEncoderForClassError as err:
                        class_name_error.error = err.kind
                    except bf_errors.DuplicateVectorError:
                        pass
                    except bf_errors.BaseAPIError as err:
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
        BrainFrameMessage.information(
            parent=parent,
            title=message_title,
            message=message
        ).exec()
