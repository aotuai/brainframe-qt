from typing import Optional, List

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import Encoding


class EncodingStubMixIn(Stub):
    """Provides stubs to call APIs that handle encodings."""

    def get_encodings(self, identity_id: Optional[int] = None,
                      class_name: Optional[str] = None) -> List[Encoding]:
        """Gets all encodings from the server that match the given filters.

        :param identity_id: If specified, only encodings attached to this
            identity will be returned
        :param class_name: If specified, only encodings for the given class
            name will be returned
        :return: All encodings that match this filter
        """
        req = f"/api/encodings"
        params = {}
        if identity_id is not None:
            params["identity_id"] = identity_id
        if class_name is not None:
            params["class_name"] = class_name

        encodings = self._get(req, params=params)
        encodings = [Encoding.from_dict(e) for e in encodings]

        return encodings

    def get_encoding_class_names(self, identity_id: Optional[int] = None) \
            -> List[str]:
        """Get all unique class names for encodings that match the given
        filter.

        :param identity_id: If specified, only class names for encodings
            attached to this identity will be returned
        :return: All class names from encodings that match this filter
        """
        req = f"/api/encodings"
        params = {"fields": "class_name"}
        if identity_id is not None:
            params["identity_id"] = identity_id

        encodings = self._get(req, params=params)
        class_names = [e["class_name"] for e in encodings]

        return class_names

    def get_encoding(self, encoding_id) -> Encoding:
        """Get the encoding with the given ID.

        :param encoding_id: The encoding ID to get an encoding for
        :return: The corresponding encoding
        """
        req = f"/api/encodings/{encoding_id}"

        encoding = self._get(req)
        return Encoding.from_dict(encoding)

    def delete_encoding(self, encoding_id):
        """Deletes the encoding with the given ID.

        :param encoding_id: The ID of the encoding to delete
        """
        req = f"/api/encodings/{encoding_id}"
        self._delete(req)

    def delete_encodings(self, identity_id=None, class_name=None):
        """Deletes all encodings that match the given filter.

        :param identity_id: If specified, only encodings that are associated
            with this identity will be deleted
        :param class_name: If specified, only encodings that are for this class
            will be deleted
        """
        req = f"/api/encodings"

        params = {}
        if identity_id is not None:
            params["identity_id"] = identity_id
        if class_name is not None:
            params["class_name"] = class_name

        self._delete(req, params)
