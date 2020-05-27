from .all_resource_paths import route_path

ui_dir = route_path("brainframe", "client", "ui")

###############################################################################
# Main Window
###############################################################################

# MainWindow
main_window_dir = route_path(ui_dir / "main_window")
main_window_qss = route_path(main_window_dir / "main_window.qss")

# ToolBar
toolbar_dir = route_path(main_window_dir / "toolbar")

###############################################################################
# Activities
###############################################################################

activity_dir = route_path(main_window_dir / "activities")

# Stream Activity
stream_activity_dir = route_path(activity_dir / "stream_activity")
stream_activity_qss = route_path(stream_activity_dir / "stream_activity.qss")

# Video Thumbnail View
video_thumbnail_view_dir = route_path(main_window_dir / "video_thumbnail_view")
video_thumbnail_view_qss = route_path(video_thumbnail_view_dir
                                      / "video_thumbnail_view.qss")

# Stream Configuration
stream_configuration_dir = route_path(activity_dir / "stream_configuration")
stream_configuration_qss = route_path(stream_configuration_dir
                                      / "stream_configuration.qss")

###############################################################################
# Dialog
###############################################################################

dialog_dir = route_path(ui_dir / "dialogs")

alarm_view_dir = route_path(dialog_dir / "alarm_view")
alarm_view_qss = route_path(alarm_view_dir / "alarm_view.qss")

###############################################################################
# BrainFrame Resources
###############################################################################

resource_dir = route_path(ui_dir / "resources")
ui_elements_dir = route_path(resource_dir / "ui_elements")

# Widgets
widget_resource_dir = route_path(ui_elements_dir / "widgets")

# Containers
container_resource_dir = route_path(ui_elements_dir / "containers")
sidebar_dock_widget_qss = route_path(
    container_resource_dir / "sidebar_dock_widget" / "sidebar_dock_widget.qss")

###############################################################################
# Alert Resources
###############################################################################

# AlarmBundle
alarm_bundle_dir = route_path(resource_dir / "alarms" / "alarm_bundle")
alarm_bundle_qss = route_path(alarm_bundle_dir / "alarm_bundle.qss")

# Alarm bundle header
bundle_header_dir = route_path(alarm_bundle_dir / "bundle_header")
bundle_header_qss = route_path(bundle_header_dir / "bundle_header.qss")

# AlarmCard
alarm_card_dir = route_path(alarm_bundle_dir / "alarm_card")
alarm_card_qss = route_path(alarm_card_dir / "alarm_card.qss")
alert_log_qss = route_path(alarm_card_dir / "alert_log" / "alert_log.qss")

# Alarm header
alarm_header_dir = route_path(alarm_card_dir / "alarm_header")
alarm_header_qss = route_path(alarm_header_dir / "alarm_header.qss")

# Alert log entry
alert_log_entry_dir = route_path(
    alarm_card_dir / "alert_log" / "alert_log_entry")
alert_log_entry_qss = route_path(alert_log_entry_dir / "alert_log_entry.qss")

# Alert header
alert_header_dir = route_path(alert_log_entry_dir / "alert_header")
alert_header_qss = route_path(alert_header_dir / "alert_header.qss")

# Alert preview
alert_preview_dir = route_path(alert_log_entry_dir / "alert_preview")
alert_preview_qss = route_path(alert_preview_dir / "alert_preview.qss")

# Alert detail
alert_detail_dir = route_path(alert_preview_qss.parent / "alert_detail")
alert_detail_qss = route_path(alert_detail_dir / "alert_detail.qss")
