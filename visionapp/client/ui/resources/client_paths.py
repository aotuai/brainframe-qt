from pathlib import Path

# UI Paths
ui                       = Path("ui")

# Main Window
main_window_dir          = Path(ui                      , "main_window"            )
main_window_ui           = Path(main_window_dir         , "main_window.ui"         )

toolbar_dir              = Path(main_window_dir         , "toolbar"                )
toolbar_ui               = Path(toolbar_dir             , "toolbar.ui"             )

video_expanded_view_dir  = Path(main_window_dir         , "video_expanded_view"    )
video_expanded_view_ui   = Path(video_expanded_view_dir , "video_expanded_view.ui" )

alert_log_dir            = Path(video_expanded_view_dir , "alert_log"              )
alert_log_ui             = Path(alert_log_dir           , "alert_log.ui"           )

video_thumbnail_view_dir = Path(main_window_dir         , "video_thumbnail_view"   )
video_thumbnail_view_ui  = Path(video_thumbnail_view_dir, "video_thumbnail_view.ui")

# Dialogs
dialogs_dir              = Path(ui                      , "dialogs"                )

stream_configuration_dir = Path(dialogs_dir             , "stream_configuration"   )
stream_configuration_ui  = Path(stream_configuration_dir, "stream_configuration.ui")

alarm_creation_dir       = Path(dialogs_dir             , "alarm_creation"         )
alarm_creation_ui        = Path(alarm_creation_dir      , "alarm_creation.ui"      )

task_configuration_dir   = Path(dialogs_dir             , "task_configuration"     )
task_configuration_ui    = Path(task_configuration_dir  , "task_configuration.ui"  )

zone_list_dir            = Path(task_configuration_dir  , "zone_list"              )
zone_list_ui             = Path(zone_list_dir           , "zone_list.ui"           )

