from .all_resource_paths import route_path

ui_dir = route_path("brainframe", "client", "ui")

###############################################################################
# Dialog
###############################################################################

dialog_dir = route_path(ui_dir / "dialogs")

alarm_view_dir = route_path(dialog_dir / "alarm_view")
alarm_view_qss = route_path(alarm_view_dir / "alarm_view.qss")

###############################################################################
# Resources
###############################################################################

resource_dir = route_path(ui_dir / "resources")

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
