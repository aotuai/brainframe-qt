from .all_resource_paths import route_path

ui_dir = route_path("brainframe", "client", "ui")

# Main Window
main_window_dir            = route_path(ui_dir                    , "main_window"              )

video_expanded_view_dir    = route_path(main_window_dir           , "video_expanded_view"      )
video_expanded_view_ui     = route_path(video_expanded_view_dir   , "video_expanded_view.ui"   )

alert_log_dir              = route_path(video_expanded_view_dir   , "alert_log"                )
alert_log_ui               = route_path(alert_log_dir             , "alert_log.ui"             )

video_thumbnail_view_dir   = route_path(main_window_dir           , "video_thumbnail_view"     )
video_thumbnail_view_ui    = route_path(video_thumbnail_view_dir  , "video_thumbnail_view.ui"  )

thumbnail_grid_layout_dir  = route_path(video_thumbnail_view_dir  , "thumbnail_grid_layout"    )
thumbnail_grid_layout_ui   = route_path(thumbnail_grid_layout_dir , "thumbnail_grid_layout.ui" )

# Activities

activity_dir               = route_path(main_window_dir           , "activities"               )

stream_configuration_dir   = route_path(activity_dir              , "stream_configuration"     )
stream_configuration_ui    = route_path(stream_configuration_dir  , "stream_configuration.ui"  )

identity_configuration_dir = route_path(activity_dir              , "identity_configuration"   )
identity_configuration_ui  = route_path(identity_configuration_dir, "identity_configuration.ui")
identity_error_popup_dir   = route_path(identity_configuration_dir, "identity_error_popup"     )
identity_error_popup_ui    = route_path(identity_error_popup_dir  , "identity_error_popup.ui"  )
directory_selector_dir     = route_path(identity_configuration_dir, "directory_selector"       )
directory_selector_ui      = route_path(directory_selector_dir    , "directory_selector.ui"    )
identity_paginator_dir     = route_path(identity_configuration_dir, "identity_grid_paginator"  )
identity_entry_dir         = route_path(identity_paginator_dir    , "identity_entry"           )
identity_entry_ui          = route_path(identity_entry_dir        , "identity_entry.ui"        )
identity_search_filter_dir = route_path(identity_configuration_dir, "identity_search_filter"   )
identity_search_filter_ui  = route_path(identity_search_filter_dir, "identity_search_filter.ui")
encoding_list_dir          = route_path(identity_configuration_dir, "encoding_list"            )
encoding_list_ui           = route_path(encoding_list_dir         , "encoding_list.ui"         )
encoding_entry_dir         = route_path(encoding_list_dir         , "encoding_entry"           )
encoding_entry_ui          = route_path(encoding_entry_dir        , "encoding_entry.ui"        )
identity_info_dir          = route_path(identity_configuration_dir, "identity_info"            )
identity_info_ui           = route_path(identity_info_dir         , "identity_info.ui"         )

# Dialogs
dialogs_dir                = route_path(ui_dir                    , "dialogs"                  )

about_page_dir             = route_path(dialogs_dir               , "about_page"               )
about_page_ui              = route_path(about_page_dir            , "about_page.ui"            )

alarm_creation_dir         = route_path(dialogs_dir               , "alarm_creation"           )
alarm_creation_ui          = route_path(alarm_creation_dir        , "alarm_creation.ui"        )

alert_entry_popup_dir      = route_path(dialogs_dir               , "alert_entry_popup"        )
alert_entry_popup_ui       = route_path(alert_entry_popup_dir     , "alert_entry_popup.ui"     )

license_agreement_dir      = route_path(dialogs_dir               , "license_agreement"        )
license_agreement_ui       = route_path(license_agreement_dir     , "license_agreement.ui"     )

plugin_config_dir          = route_path(dialogs_dir               , "plugin_configuration"     )
plugin_config_dialog_ui    = route_path(plugin_config_dir         , "plugin_config.ui"         )
plugin_list_dir            = route_path(plugin_config_dir         , "plugin_list"              )
plugin_list_ui             = route_path(plugin_list_dir           , "plugin_list.ui"           )
plugin_list_item_dir       = route_path(plugin_list_dir           , "plugin_list_item"         )
plugin_list_item_ui        = route_path(plugin_list_item_dir      , "plugin_list_item.ui"      )
plugin_options_dir         = route_path(plugin_config_dir         , "plugin_options"           )
plugin_options_ui          = route_path(plugin_options_dir        , "plugin_options.ui"        )

server_configuration_dir   = route_path(dialogs_dir               , "server_configuration"     )
server_configuration_ui    = route_path(server_configuration_dir  , "server_configuration.ui"  )

task_configuration_dir     = route_path(dialogs_dir               , "task_configuration"       )
task_configuration_ui      = route_path(task_configuration_dir    , "task_configuration.ui"    )

client_configuration_dir   = route_path(dialogs_dir               , "client_configuration"     )
client_configuration_ui    = route_path(client_configuration_dir  , "client_configuration.ui"  )

zone_list_dir              = route_path(task_configuration_dir    , "zone_list"                )
zone_list_ui               = route_path(zone_list_dir             , "zone_list.ui"             )

# Resources
ui_elements_dir            = route_path(ui_dir                    , "resources", "ui_elements" )
button_resources_dir       = route_path(ui_elements_dir           , "buttons"                  )
containers_resources_dir   = route_path(ui_elements_dir           , "containers"               )
paginator_ui               = route_path(containers_resources_dir  , "paginator.ui"             )
