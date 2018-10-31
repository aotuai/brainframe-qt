from typing import Tuple
from io import BytesIO

from PIL import Image
import numpy as np
import cv2

from brainframe.client.api.stubs.stub import Stub


class StorageStubMixin(Stub):
    """Provides stubs to call APIs for managing binary blob storage."""

    def get_storage_data(self, storage_id) -> Tuple[bytes, str]:
        """Returns the data with the given storage ID.

        :param storage_id: The ID of the storage object to get
        :return: The data and MIME type of that data
        """
        req = f"/api/storage/{storage_id}"
        return self._get_raw(req)

    def get_storage_data_as_image(self, storage_id) -> np.ndarray:
        """Gets the data with the given storage ID and attempts to load it as
        an image with OpenCV.

        :param storage_id: The ID of the storage object to get
        :return: A numpy array in OpenCV format
        """
        data, _ = self.get_storage_data(storage_id)
        return cv2.imdecode(np.fromstring(data, np.uint8),
                            cv2.IMREAD_COLOR)

    def new_storage(self, data: bytes, mime_type: str) -> int:
        """Stores the given data.

        :param data: The data to store
        :param mime_type: The MIME type of the data
        :return: The storage ID
        """
        req = r"/api/storage"

        storage_id = self._post_raw(req, data, mime_type)
        return storage_id

    def new_storage_as_image(self, data: bytes) -> int:
        """Stores the given image data, and inspects it to figure out what the
        MIME type of the data.

        :param data: The image data to store
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

        return self.new_storage(data, mime_type)
