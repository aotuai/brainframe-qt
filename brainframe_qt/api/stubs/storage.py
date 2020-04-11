from typing import Tuple, BinaryIO, Union, Iterable
from io import BytesIO

import numpy as np
import ujson
from PIL import Image

from brainframe.client.api import image_utils
from brainframe.client.api.stubs.base_stub import BaseStub, DEFAULT_TIMEOUT


class StorageStubMixin(BaseStub):
    """Provides stubs to call APIs for managing binary blob storage."""

    def get_storage_data(self, storage_id,
                         timeout=DEFAULT_TIMEOUT) -> Tuple[bytes, str]:
        """Returns the data with the given storage ID.

        :param storage_id: The ID of the storage object to get
        :param timeout: The timeout to use for this request
        :return: The data and MIME type of that data
        """
        req = f"/api/storage/{storage_id}"
        resp = self._get(req, timeout)

        return resp.content, resp.headers["Content-Type"]

    def get_storage_data_as_image(self, storage_id,
                                  timeout=DEFAULT_TIMEOUT) -> np.ndarray:
        """Gets the data with the given storage ID and attempts to load it as
        an image with OpenCV.

        :param storage_id: The ID of the storage object to get
        :param timeout: The timeout to use for this request
        :return: A numpy array in OpenCV format
        """
        data, _ = self.get_storage_data(storage_id, timeout=timeout)
        return image_utils.decode(data)

    def new_storage(self, data: Union[bytes, BinaryIO, Iterable],
                    mime_type: str,
                    timeout=DEFAULT_TIMEOUT) -> int:
        """Stores the given data.

        :param data: The data to store, either as bytes or as a file-like
        :param mime_type: The MIME type of the data
        :param timeout: The timeout to use for this request
        :return: The storage ID
        """
        req = r"/api/storage"

        storage_id_json = self._post(req, timeout, data, mime_type).content
        return ujson.loads(storage_id_json)

    def new_storage_as_image(self, data: bytes,
                             timeout=DEFAULT_TIMEOUT) -> int:
        """Stores the given image data, and inspects it to figure out what the
        MIME type of the data.

        :param data: The image data to store
        :param timeout: The timeout to use for this request
        :return: The storage ID
        """
        try:
            pil_image = Image.open(BytesIO(data))

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

        return self.new_storage(data, mime_type, timeout=timeout)
