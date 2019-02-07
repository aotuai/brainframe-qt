from typing import List, Dict
import ujson

import numpy as np
import cv2

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import Detection


class ProcessImageStubMixIn(Stub):
    """Provides stubs to call APIs that run processing on a single frame."""

    def process_image(self, img_bgr: np.ndarray,
                      plugins: List[str],
                      options: Dict[str, Dict[str, object]]) \
            -> List[Detection]:
        """Process a single image using the given configuration.
        :param img_bgr: The image to process
        :param plugins: The plugins to enable while processing the image
        :param options: Plugin options, where the key is a plugin name and the
            value is a dict with key-value pairs for each option and its
            corresponding value. Any specified options will override the global
            option values
        :return: All detections in the image
        """
        req = f"/api/process_image"

        metadata = {
            "plugins": plugins,
            "options": options
        }
        metadata = ujson.dumps(metadata)

        # Encode the image
        _, img_bytes = cv2.imencode(".jpg", img_bgr)
        img_bytes = bytes(img_bytes.tostring())

        files = {
            "image": ("image.jpg",
                      img_bytes,
                      "image/jpeg"),
            "metadata": ("metadata.json",
                         metadata.encode("utf-8"),
                         "application/json")}

        resp = self._post_multipart(req, files)
        return [Detection.from_dict(d) for d in resp]
