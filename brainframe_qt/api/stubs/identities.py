from typing import List

from io import BytesIO
from PIL import Image
import ujson
import numpy as np
import cv2

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import Identity


class IdentityStubMixin(Stub):
    """Provides stubs to call APIs that create and update identities, as well as
    add new examples of the identity in image or vector form.
    """

    def get_identity(self, identity_id: int) -> Identity:
        """Gets the identity with the given ID.
        :param identity_id: The ID of the identity to get
        :return: Identity
        """
        req = f"/api/identities/{identity_id}"
        identity = self._get(req)

        return Identity.from_dict(identity)

    def get_identities(self, unique_name=None) -> List[Identity]:
        """Returns all identities from the server.
        :return: List of identities
        """
        req = f"/api/identities"
        params = {"unique_name": unique_name} if unique_name else None
        identities = self._get(req, params=params)
        identities = [Identity.from_dict(d) for d in identities]

        return identities

    def set_identity(self, identity: Identity) -> Identity:
        """Updates or creates an identity. If the identity does not already
        exist, identity.id must be None. The returned identity will have an
        assigned ID.
        :param identity: The identity to save or create
        :return: the saved identity
        """
        req = f"/api/identities"
        saved = self._post_codec(req, identity)
        return Identity.from_dict(saved)

    def new_identity_image(self, identity_id: int, class_name: str,
                           image: bytes) -> int:
        """Saves and encodes an image under the identity with the given ID.

        :param identity_id: Identity to associate the image with
        :param class_name: The type of object this image shows and should be
            encoded for
        :param image: The image to save
        :return: The image ID
        """
        req = f"/api/identities/{identity_id}/classes/{class_name}/images"

        # Try to figure out the image type. If we can't figure it out, send it
        # as raw data to the server in case the server supports it

        try:
            pil_image = Image.open(BytesIO(image))

            if pil_image.format == "JPEG":
                mime_type = "image/jpeg"
            elif pil_image.format == "PNG":
                mime_type = "image/png"
            else:
                mime_type = "application/octet-stream"
        except IOError:
            # TODO(Tyler Compton): This failure mode is stupid but I don't want
            # two ways for this call to fail when an invalid image is passed to
            # it. Figure out a better way.
            mime_type = "application/octet-stream"

        image_id = self._post_raw(req, image, mime_type)
        return image_id

    def new_identity_vector(self, identity_id: int, class_name: str,
                            vector: List[float]) -> int:
        """Saves the given vector under the identity with the given ID. In this
        case, a vector is simply a list of one or more numbers that describe
        some object in an image.

        :param identity_id: Identity to associate the vector with
        :param class_name: The type of object this vector describes
        :param vector: The vector to save
        :return: The vector ID
        """
        req = f"/api/identities/{identity_id}/classes/{class_name}/vectors"

        return self._post_json(req, ujson.dumps(vector))

    def get_identity_image(self, identity_id: int, class_name: str,
                           image_id: int) -> np.ndarray:
        """Returns the image with the given image ID.

        :param identity_id: The ID of the identity that the image is associated
            with
        :param class_name: The class name that this image was encoded for
        :param image_id: The ID of the image
        :return: The image as loaded by OpenCV
        """
        req = (f"/api/identities/{identity_id}"
               f"/classes/{class_name}"
               f"/images/{image_id}")
        image_bytes = self._get_raw(req)

        return cv2.imdecode(np.fromstring(image_bytes, np.uint8),
                            cv2.IMREAD_COLOR)

    def get_image_ids_for_identity(self, identity_id, class_name) -> List[int]:
        """Returns all IDs for the identity with the given ID that are for
        encodings of the given class name.

        :param identity_id: The ID of the identity to look for images under
        :param class_name: The class name to look for images encoded for
        :return: List of image IDs
        """
        req = (f"/api/identities/{identity_id}"
               f"/classes/{class_name}"
               f"/images")
        image_ids = self._get(req)
        return image_ids
