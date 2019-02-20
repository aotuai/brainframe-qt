"""
This module mirrors certain OpenCV functions with pillow as a backend
"""
from io import BytesIO

import numpy as np
from PIL import Image


def decode(img_bytes: bytes) -> np.ndarray:
    rgb_img = Image.open(BytesIO(img_bytes))

    # Load as numpy array
    bgr_arr = np.asarray(rgb_img, dtype=np.uint8)

    # Convert from RGB to BGR
    bgr_arr = flip_channels(bgr_arr)

    # Return a fresh copy instead of a "memoryview" object...
    return bgr_arr.copy()


def encode(format: str, image_bgr_arr: np.ndarray):
    img_rgb_arr = flip_channels(image_bgr_arr)
    image = Image.fromarray(img_rgb_arr)
    img_bytes = BytesIO()

    image.save(img_bytes, format=format)
    img_bytes = img_bytes.getvalue()

    # import cv2
    # cv2.imshow("ayy", decode(img_bytes))
    # cv2.waitKey(10000)
    return img_bytes


def flip_channels(img_arr):
    return img_arr[..., ::-1]
