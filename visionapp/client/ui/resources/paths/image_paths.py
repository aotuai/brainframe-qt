import os
from pathlib import Path


# TODO: Figure out how to get rid of the visionapp/client from top level path
image_dir = Path("ui/resources/images")
if not os.getcwd().endswith("client"):
    image_dir = Path("visionapp", "client", image_dir)


# Icons
new_stream_icon   = Path(image_dir, "new_stream_icon.jpg")
cat_test_video    = Path(image_dir, "cat.jpg"            )
camera_test_video = Path(image_dir, "camera.jpeg"        )