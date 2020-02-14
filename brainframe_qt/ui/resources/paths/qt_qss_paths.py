from .all_resource_paths import route_path

ui_dir = route_path("brainframe", "client", "ui")

# Resources
# AlarmBundle
alarm_bundle_dir = ui_dir / "resources" / "alarms" / "alarm_bundle"
alarm_bundle_qss = alarm_bundle_dir / "alarm_bundle.qss"
bundle_header_qss = alarm_bundle_dir / "bundle_header" / "bundle_header.qss"

# AlarmCard
alarm_card_dir = alarm_bundle_dir / "alarm_card"
alarm_card_qss = alarm_card_dir / "alarm_card.qss"
alarm_preview_qss = alarm_card_dir / "alarm_preview" / "alarm_preview.qss"
alert_log_qss = alarm_card_dir / "alert_log" / "alert_log.qss"
alert_log_entry_qss = alarm_card_dir / "alert_log" / "alert_log_entry" \
                      / "alert_log_entry.qss"
