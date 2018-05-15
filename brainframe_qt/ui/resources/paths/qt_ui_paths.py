from .all_resource_paths import route_path

ui_dir = route_path("brainframe", "client", "ui")

# Main Window
main_window_dir            = route_path(ui_dir                    , "main_window"              )
main_window_ui             = route_path(main_window_dir           , "main_window.ui"           )

toolbar_dir                = route_path(main_window_dir           , "toolbar"                  )
toolbar_ui                 = route_path(toolbar_dir               , "toolbar.ui"               )

video_expanded_view_dir    = route_path(main_window_dir           , "video_expanded_view"      )
video_expanded_view_ui     = route_path(video_expanded_view_dir   , "video_expanded_view.ui"   )

alert_log_dir              = route_path(video_expanded_view_dir   , "alert_log"                )
alert_log_ui               = route_path(alert_log_dir             , "alert_log.ui"             )

alert_log_entry_dir        = route_path(alert_log_dir             , "alert_log_entry"          )
alert_log_entry_ui         = route_path(alert_log_entry_dir       , "alert_log_entry.ui"       )

video_thumbnail_view_dir   = route_path(main_window_dir           , "video_thumbnail_view"     )
video_thumbnail_view_ui    = route_path(video_thumbnail_view_dir  , "video_thumbnail_view.ui"  )

new_stream_button_dir      = route_path(video_thumbnail_view_dir  , "new_stream_button"        )
new_stream_button_ui       = route_path(new_stream_button_dir     , "new_stream_button.ui"     )

# Dialogs
dialogs_dir                = route_path(ui_dir                    , "dialogs"                  )

alarm_creation_dir         = route_path(dialogs_dir               , "alarm_creation"           )
alarm_creation_ui          = route_path(alarm_creation_dir        , "alarm_creation.ui"        )

identity_configuration_dir = route_path(dialogs_dir               , "identity_configuration"   )
identity_configuration_ui  = route_path(identity_configuration_dir, "identity_configuration.ui")

directory_selector_dir     = route_path(identity_configuration_dir, "directory_selector"       )
directory_selector_ui      = route_path(directory_selector_dir    , "directory_selector.ui"    )

license_agreement_dir      = route_path(dialogs_dir               , "license_agreement"        )
license_agreement_ui       = route_path(license_agreement_dir     , "license_agreement.ui"     )

task_configuration_dir     = route_path(dialogs_dir               , "task_configuration"       )
task_configuration_ui      = route_path(task_configuration_dir    , "task_configuration.ui"    )

zone_list_dir              = route_path(task_configuration_dir    , "zone_list"                )
zone_list_ui               = route_path(zone_list_dir             , "zone_list.ui"             )

stream_configuration_dir   = route_path(dialogs_dir               , "stream_configuration"     )
stream_configuration_ui    = route_path(stream_configuration_dir  , "stream_configuration.ui"  )