from .all_resource_paths import register_path

ui_dir = register_path("brainframe", "client", "ui")

###############################################################################
# Main Window
###############################################################################

# MainWindow
main_window_dir = register_path(ui_dir / "main_window")
main_window_qss = register_path(main_window_dir / "main_window.qss")

# ToolBar
toolbar_dir = register_path(main_window_dir / "toolbar")

###############################################################################
# Activities
###############################################################################

activity_dir = register_path(main_window_dir / "activities")

# Stream Activity
stream_activity_dir = register_path(activity_dir
                                    / "stream_activity")
stream_view_qss = register_path(stream_activity_dir / "stream_view.qss")

# Video Thumbnail View
video_thumbnail_view_dir = register_path(
    main_window_dir / "video_thumbnail_view")
video_thumbnail_view_qss = register_path(
    video_thumbnail_view_dir / "video_thumbnail_view.qss")

# Stream Configuration
stream_configuration_dir = register_path(activity_dir / "stream_configuration")
stream_configuration_qss = register_path(
    stream_configuration_dir / "stream_configuration.qss")

###############################################################################
# Dialog
###############################################################################

dialog_dir = register_path(ui_dir / "dialogs")

alarm_view_dir = register_path(dialog_dir / "alarm_view")
alarm_view_qss = register_path(alarm_view_dir / "alarm_view.qss")

license_dialog_dir = register_path(dialog_dir / "license_dialog")
license_dialog_qss = register_path(license_dialog_dir / "license_dialog.qss")

###############################################################################
# BrainFrame Resources
###############################################################################

resource_dir = register_path(ui_dir / "resources")
ui_elements_dir = register_path(resource_dir / "ui_elements")

# Widgets
widget_resource_dir = register_path(ui_elements_dir / "widgets")

# Containers
container_resource_dir = register_path(ui_elements_dir / "containers")
sidebar_dock_widget_qss = register_path(
    container_resource_dir / "sidebar_dock_widget" / "sidebar_dock_widget.qss")

###############################################################################
# Video Resources
###############################################################################

video_items_dir = register_path(resource_dir / "video_items")

streams_items_dir = register_path(video_items_dir / "streams")
stream_widget_qss = register_path(streams_items_dir / "stream_widget.qss")


###############################################################################
# Alert Resources
###############################################################################

# AlarmBundle
alarm_bundle_dir = register_path(resource_dir / "alarms" / "alarm_bundle")
alarm_bundle_qss = register_path(alarm_bundle_dir / "alarm_bundle.qss")

# Alarm bundle header
bundle_header_dir = register_path(alarm_bundle_dir / "bundle_header")
bundle_header_qss = register_path(bundle_header_dir / "bundle_header.qss")

# AlarmCard
alarm_card_dir = register_path(alarm_bundle_dir / "alarm_card")
alarm_card_qss = register_path(alarm_card_dir / "alarm_card.qss")
alert_log_qss = register_path(alarm_card_dir / "alert_log" / "alert_log.qss")

# Alarm header
alarm_header_dir = register_path(alarm_card_dir / "alarm_header")
alarm_header_qss = register_path(alarm_header_dir / "alarm_header.qss")

# Alert log entry
alert_log_entry_dir = register_path(
    alarm_card_dir / "alert_log" / "alert_log_entry")
alert_log_entry_qss = register_path(
    alert_log_entry_dir / "alert_log_entry.qss")

# Alert header
alert_header_dir = register_path(alert_log_entry_dir / "alert_header")
alert_header_qss = register_path(alert_header_dir / "alert_header.qss")

# Alert preview
alert_preview_dir = register_path(alert_log_entry_dir / "alert_preview")
alert_preview_qss = register_path(alert_preview_dir / "alert_preview.qss")

# Alert detail
alert_detail_dir = register_path(alert_preview_qss.parent / "alert_detail")
alert_detail_qss = register_path(alert_detail_dir / "alert_detail.qss")
