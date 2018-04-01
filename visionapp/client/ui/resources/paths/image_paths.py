from pathlib import Path

from visionapp.client.ui.resources.paths.all_resource_paths import route_path, all_paths

image_dir = Path("visionapp", "client", "ui", "resources", "images")


# Images
cat_test_video     = route_path(image_dir, "cat.jpg"            )
ostrich_test_video = route_path(image_dir, "ostrich.jpg"        )
camera_test_video  = route_path(image_dir, "camera.jpeg"        )
video_not_found    = route_path(image_dir, "video_not_found.png")

# Icons
icon_dir           = route_path(image_dir, "icons"              )
new_stream_icon    = route_path( icon_dir, "new_stream.jpg"     )
alarm_icon         = route_path( icon_dir, "alarm.jpg"          )
line_icon          = route_path( icon_dir, "line.jpg"           )
region_icon        = route_path( icon_dir, "region.png"         )
settings_gear_icon = route_path( icon_dir, "settings_gear.png"  )
question_mark_icon = route_path( icon_dir, "question_mark.png"  )
trash_icon         = route_path( icon_dir, "trash.png"          )
