import typing

from PyQt5.QtCore import QTranslator, QLocale
from PyQt5.QtWidgets import QWidget
from brainframe_qt.ui.resources.paths import text_paths
from brainframe_qt.ui.resources.ui_elements.widgets.dialogs import BrainFrameMessage


class BrainFrameTranslator(QTranslator):

    LOCALE_PREFIX = "brainframe"
    LOCALE_DIR = str(text_paths.i18n_dir)

    def __init__(self):
        super().__init__()

        self.locale = QLocale.system()

        if not self.load(self.locale, self.LOCALE_PREFIX, '_', self.LOCALE_DIR):
            self._handle_missing_locale()

    def _handle_missing_locale(self):

        if self.locale.language() != self.locale.English:
            # TODO: Find a better way that doesn't rely on a _list of preferences_.
            #  If, say, zh_BA (which isn't a thing) is used, locale.name() returns
            #  zh_CN (which _is_ a real language). If there is no `zh` language, we
            #  want to throw a warning with zh_BA specified, not zh_CN. We settle
            #  for locale.uiLanguages() because it returns ['zh_BA']. Not sure if it
            #  might have other entries under some conditions.
            locale_str = self.locale.uiLanguages()[0]

            title = "Error loading language files"
            message = (
                f"Unable to load translation file for [{locale_str}] locale. Using "
                f"English as a fallback."
            )

            BrainFrameMessage.warning(
                parent=typing.cast(QWidget, None),  # No parent
                title=title,
                warning=message
            ).exec()
