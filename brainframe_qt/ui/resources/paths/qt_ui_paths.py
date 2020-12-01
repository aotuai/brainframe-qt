from .all_resource_paths import register_path

ui_dir = register_path("brainframe_qt", "ui")

# Main Window
main_window_dir            = register_path(ui_dir                    , "main_window"              )

video_expanded_view_dir    = register_path(main_window_dir           , "video_expanded_view"      )
video_expanded_view_ui     = register_path(video_expanded_view_dir   , "video_expanded_view.ui"   )

alert_log_dir              = register_path(video_expanded_view_dir   , "alert_log"                )
alert_log_ui               = register_path(alert_log_dir             , "alert_log.ui"             )

video_thumbnail_view_dir   = register_path(main_window_dir           , "video_thumbnail_view"     )

thumbnail_grid_layout_dir  = register_path(video_thumbnail_view_dir  , "thumbnail_grid_layout"    )
thumbnail_grid_layout_ui   = register_path(thumbnail_grid_layout_dir , "thumbnail_grid_layout.ui" )

# Activities

activity_dir               = register_path(main_window_dir           , "activities"               )

identity_configuration_dir = register_path(activity_dir              , "identity_configuration"   )
identity_configuration_ui  = register_path(identity_configuration_dir, "identity_configuration.ui")
identity_error_popup_dir   = register_path(identity_configuration_dir, "identity_error_popup"     )
identity_error_popup_ui    = register_path(identity_error_popup_dir  , "identity_error_popup.ui"  )
directory_selector_dir     = register_path(identity_configuration_dir, "directory_selector"       )
directory_selector_ui      = register_path(directory_selector_dir    , "directory_selector.ui"    )
identity_paginator_dir     = register_path(identity_configuration_dir, "identity_grid_paginator"  )
identity_entry_dir         = register_path(identity_paginator_dir    , "identity_entry"           )
identity_entry_ui          = register_path(identity_entry_dir        , "identity_entry.ui"        )
identity_search_filter_dir = register_path(identity_configuration_dir, "identity_search_filter"   )
identity_search_filter_ui  = register_path(identity_search_filter_dir, "identity_search_filter.ui")
encoding_list_dir          = register_path(identity_configuration_dir, "encoding_list"            )
encoding_list_ui           = register_path(encoding_list_dir         , "encoding_list.ui"         )
encoding_entry_dir         = register_path(encoding_list_dir         , "encoding_entry"           )
encoding_entry_ui          = register_path(encoding_entry_dir        , "encoding_entry.ui"        )
identity_info_dir          = register_path(identity_configuration_dir, "identity_info"            )
identity_info_ui           = register_path(identity_info_dir         , "identity_info.ui"         )

# Dialogs
dialogs_dir                = register_path(ui_dir                    , "dialogs"                  )

about_page_dir             = register_path(dialogs_dir               , "about_page"               )
about_page_ui              = register_path(about_page_dir            , "about_page.ui"            )

alarm_creation_dir         = register_path(dialogs_dir               , "alarm_creation"           )
alarm_creation_ui          = register_path(alarm_creation_dir        , "alarm_creation.ui"        )

alert_entry_popup_dir      = register_path(dialogs_dir               , "alert_entry_popup"        )
alert_entry_popup_ui       = register_path(alert_entry_popup_dir     , "alert_entry_popup.ui"     )

license_agreement_dir      = register_path(dialogs_dir               , "license_agreement"        )
license_agreement_ui       = register_path(license_agreement_dir     , "license_agreement.ui"     )

capsule_config_dir         = register_path(dialogs_dir               , "capsule_configuration"    )
capsule_config_dialog_ui   = register_path(capsule_config_dir        , "capsule_config.ui"        )
capsule_list_dir           = register_path(capsule_config_dir        , "capsule_list"             )
capsule_list_ui            = register_path(capsule_list_dir          , "capsule_list.ui"          )
capsule_list_item_dir      = register_path(capsule_list_dir          , "capsule_list_item"        )
capsule_list_item_ui       = register_path(capsule_list_item_dir     , "capsule_list_item.ui"     )
capsule_options_dir        = register_path(capsule_config_dir        , "capsule_options"          )
capsule_options_ui         = register_path(capsule_options_dir       , "capsule_options.ui"       )

server_configuration_dir   = register_path(dialogs_dir               , "server_configuration"     )
server_configuration_ui    = register_path(server_configuration_dir  , "server_configuration.ui"  )

task_configuration_dir     = register_path(dialogs_dir               , "task_configuration"       )
task_configuration_ui      = register_path(task_configuration_dir    , "task_configuration.ui"    )

client_configuration_dir   = register_path(dialogs_dir               , "client_configuration"     )
client_configuration_ui    = register_path(client_configuration_dir  , "client_configuration.ui"  )

zone_list_dir              = register_path(task_configuration_dir    , "zone_list"                )
zone_list_ui               = register_path(zone_list_dir             , "zone_list.ui"             )

# Resources
ui_elements_dir            = register_path(ui_dir                    , "resources", "ui_elements" )
button_resources_dir       = register_path(ui_elements_dir           , "buttons"                  )
containers_resources_dir   = register_path(ui_elements_dir           , "containers"               )
paginator_ui               = register_path(containers_resources_dir  , "paginator.ui"             )
