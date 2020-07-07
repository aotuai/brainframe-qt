from PyQt5.QtWidgets import QPushButton, QGridLayout, QMessageBox

from brainframe.client.api_utils import api

from .base_capsule_options import BaseCapsuleOptionsWidget


class GlobalCapsuleOptionsWidget(BaseCapsuleOptionsWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.window().setWindowTitle(self.tr("Global Capsule Options"))
        self.override_label.hide()

        self._reset_overriding_btn = QPushButton(
            self.tr("Reset All Overriding Streams"),
            parent=self)
        self._reset_to_defaults_btn = QPushButton(
            self.tr("Reset to Defaults"),
            parent=self)
        # Add the button to the buttons grid
        self.buttons_grid.addWidget(self._reset_to_defaults_btn, 0, 1)
        self.buttons_grid.addWidget(self._reset_overriding_btn, 1, 1)

        # Link buttons to functions
        self._reset_to_defaults_btn.clicked.connect(
            self.on_reset_to_defaults)
        self._reset_overriding_btn.clicked.connect(
            self.on_reset_overriding_streams)

    def on_reset_to_defaults(self):
        """
        Reset all values to default after prompting the user

        Connected to:
        - QPushButton -- Dynamic
          self._reset_to_defaults_btn.clicked.connect
        """
        title = self.tr("Reset to Defaults")

        default_values = {key: option.default
                          for key, option in
                          api.get_capsule(self.current_capsule).options.items()}

        # Check if there are any changed options
        changed_options = []
        for option_item in self.option_items:
            if option_item.val != default_values[option_item.option_name]:
                changed_options.append(option_item.option_name)

        # Prompt the user appropriately
        if len(changed_options):
            desc = self.tr("The following options will be reset to default:")
            desc += "\n\t" + "\n\t".join(changed_options)
            result = QMessageBox.question(self, title, desc)
            if result != QMessageBox.Yes:
                # The user cancelled, so exit early.
                return

            # Change the options to default
            for option_item in self.option_items:
                option_item.set_val(default_values[option_item.option_name])

            # Change the 'enabled' to default
            self.enabled_option.set_val(True)
        else:
            desc = self.tr("There are no changes to reset")
            QMessageBox.information(self, title, desc)

    def on_reset_overriding_streams(self):
        """
        Reset all values to default after prompting the user

        Connected to:
        - QPushButton -- Dynamic
          self._reset_overriding_btn.clicked.connect
        """
        all_stream_ids = [s.id for s in api.get_stream_configurations()]

        # Check if any streams override this
        changed_stream_ids = []
        for stream_id in all_stream_ids:
            # Check if capsule options or capsule activity is changed
            # server-side
            opts = api.get_capsule_option_vals(
                capsule_name=self.current_capsule,
                stream_id=stream_id)
            is_active = api.is_capsule_active(
                capsule_name=self.current_capsule,
                stream_id=stream_id)

            if len(opts) or is_active is not None:
                changed_stream_ids.append(stream_id)

        title = self.tr("Reset All Overriding Streams")
        if len(changed_stream_ids):
            desc = self.tr("The following streams have overrides that will be "
                           "cleared:")
            desc += "\n\t"

            stream_names = [s.name for s in api.get_stream_configurations()
                            if s.id in changed_stream_ids]

            desc += ", \n\t".join(stream_names)
            result = QMessageBox.question(self, title, desc)
            if result != QMessageBox.Yes:
                # The user cancelled, so exit early.
                return

            # Change the options to default
            for stream_id in changed_stream_ids:
                api.set_capsule_option_vals(
                    capsule_name=self.current_capsule,
                    stream_id=stream_id,
                    option_vals={})
                api.set_capsule_active(
                    capsule_name=self.current_capsule,
                    stream_id=stream_id,
                    active=None)
        else:
            desc = self.tr("There are no streams that override the global "
                           "options for this capsule.")
            QMessageBox.information(
                self, title, desc)
