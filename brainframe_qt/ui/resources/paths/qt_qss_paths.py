from .all_resource_paths import route_path

ui_dir = route_path("brainframe", "client", "ui")

###############################################################################
# Dialog
###############################################################################

dialog_dir = ui_dir / "dialogs"

alarm_view_dir = dialog_dir / "alarm_view"
alarm_view_qss = alarm_view_dir / "alarm_view.qss"


###############################################################################
# Resources
###############################################################################

resource_dir = ui_dir / "resources"

# AlarmBundle
alarm_bundle_dir = resource_dir / "alarms" / "alarm_bundle"
alarm_bundle_qss = alarm_bundle_dir / "alarm_bundle.qss"
bundle_header_qss = alarm_bundle_dir / "bundle_header" / "bundle_header.qss"

# AlarmCard
alarm_card_dir = alarm_bundle_dir / "alarm_card"
alarm_card_qss = alarm_card_dir / "alarm_card.qss"
alarm_preview_qss = alarm_card_dir / "alarm_preview" / "alarm_preview.qss"
alert_log_qss = alarm_card_dir / "alert_log" / "alert_log.qss"
alert_log_entry_qss = alarm_card_dir / "alert_log" / "alert_log_entry" \
                      / "alert_log_entry.qss"
alert_header_qss = alarm_card_dir / "alert_log" / "alert_log_entry" \
                   / "alert_header" / "alert_header.qss"
