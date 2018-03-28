from pathlib import Path


image_dir = Path("visionapp", "client", "ui", "resources", "images")


# Images
cat_test_video     = Path(image_dir, "cat.jpg"            )
ostrich_test_video = Path(image_dir, "ostrich.jpg"        )
camera_test_video  = Path(image_dir, "camera.jpeg"        )
video_not_found    = Path(image_dir, "video_not_found.png")

# Icons
icon_dir           = Path(image_dir, "icons"              )
new_stream_icon    = Path( icon_dir, "new_stream.jpg"     )
alarm_icon         = Path( icon_dir, "alarm.jpg"          )
line_icon          = Path( icon_dir, "line.jpg"           )
region_icon        = Path( icon_dir, "region.png"         )
settings_gear_icon = Path( icon_dir, "settings_gear.png"  )
question_mark_icon = Path( icon_dir, "question_mark.png"  )