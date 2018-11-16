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
                           storage_id: int):
        """Saves and encodes an image under the identity with the given ID.

        :param identity_id: Identity to associate the image with
        :param class_name: The type of object this image shows and should be
            encoded for
        :param storage_id: The ID of the image in storage to encode
        """
        req = f"/api/identities/{identity_id}/images"
        req_obj = {
            "class_name": class_name,
            "storage_id": storage_id
        }
        self._post_json(req, ujson.dumps(req_obj))

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
        req = f"/api/identities/{identity_id}/vectors"

        encoded_obj = {
            "class_name": class_name,
            "vector": vector
        }
        return self._post_json(req, ujson.dumps(encoded_obj))

    def get_image_ids_for_identity(self, identity_id, class_name=None) \
            -> List[int]:
        """Returns all image storage IDs that are encoded for this identity.

        :param identity_id: The ID of the identity to look for images under
        :param class_name: Will filter images by ones that are encoded for this
            class name, if provided
        :return: List of storage IDs
        """
        req = f"/api/identities/{identity_id}/images"
        params = {"class_name": class_name} if class_name else None
        image_ids = self._get(req, params=params)
        return image_ids
