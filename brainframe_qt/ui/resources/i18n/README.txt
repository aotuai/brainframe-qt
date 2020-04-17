# Introduction

This is a guide on how to update existing translations or add new ones for the
UI.

# Dependencies

We use Qt's i18n support tools to manage translations. Make sure that you have
the packages outlined in the main README for UI development installed.

# Usage

After adding a new file or changing an existing file that needs translations or to add a new language,
edit and run the "Compile QT Resources" run configuration. If you're not using PyCharm, run
`compile_qt_resources.py` from within the client dir.

This script will fail on the "compiling" step until all translations are marked as "finished".
For development, add the "--tr-dev" flag.

After running the script, this directory is populated with new .ts files (if
new languages were added) and the existing .ts files are updated to contain
any new strings that need translation.

Using `linguist`, open the .ts files and add translations for the new languages
and strings (including English, but just click the confirm checkbox).
