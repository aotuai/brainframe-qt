from pathlib import Path

from .all_resource_paths import route_path

image_dir = Path("visionapp", "client", "ui", "resources", "images")


# Images
video_not_found      = route_path(image_dir, "video_not_found.png"     )
connecting_to_stream = route_path(image_dir, "connecting_to_stream.png")
stream_finished      = route_path(image_dir, "stream_finished.png"     )
splash_screen        = route_path(image_dir, "splash_screen.jpg"       )

# Icons
icon_dir           = route_path(image_dir, "icons"              )
new_stream_icon    = route_path( icon_dir, "new_stream.jpg"     )
alarm_icon         = route_path( icon_dir, "alarm.jpg"          )
alert_icon         = route_path( icon_dir, "alert.png"          )
line_icon          = route_path( icon_dir, "line.jpg"           )
region_icon        = route_path( icon_dir, "region.png"         )
settings_gear_icon = route_path( icon_dir, "settings_gear.png"  )
question_mark_icon = route_path( icon_dir, "question_mark.png"  )
trash_icon         = route_path( icon_dir, "trash.png"          )
application_icon   = route_path( icon_dir, "app_icon.png"       )