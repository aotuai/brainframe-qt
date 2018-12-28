from .all_resource_paths import route_path

image_dir = route_path("brainframe", "client", "ui", "resources", "images")


# Images
connecting_to_stream      = route_path(image_dir, "connecting_to_stream.png")
connection_lost           = route_path(image_dir, "connection_lost.png"     )
splash_screen             = route_path(image_dir, "splash_screen.png"       )
background                = route_path(image_dir, "background.svg"          )
error                     = route_path(image_dir, "error_message.png"       )

# Icons
icon_dir                  = route_path(image_dir, "icons"                   )
alarm_icon                = route_path( icon_dir, "alarm.svg"               )
alert_icon                = route_path( icon_dir, "alert.svg"               )
application_icon          = route_path( icon_dir, "app_icon.png"            )
folder_icon               = route_path( icon_dir, "folder.svg"              )
information_icon          = route_path( icon_dir, "information.svg"         )
line_icon                 = route_path( icon_dir, "line.svg"                )
new_stream_icon           = route_path( icon_dir, "new_stream.svg"          )
question_mark_icon        = route_path( icon_dir, "question_mark.svg"       )
region_icon               = route_path( icon_dir, "region.svg"              )
settings_gear_icon        = route_path( icon_dir, "settings_gear.svg"       )
trash_icon                = route_path( icon_dir, "trash.svg"               )
global_plugin_conf_icon   = route_path( icon_dir, "global_plugin_config.svg")
stream_plugin_conf_icon   = route_path( icon_dir, "stream_plugin_config.svg")