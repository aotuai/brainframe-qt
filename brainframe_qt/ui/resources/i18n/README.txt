# Introduction

This is a guide on how to update existing translations or add new ones for the
UI.

# Dependencies

We use Qt's i18n support tools to manage translations. Make sure that you have
the packages outlined in the main README for UI development installed.

# Usage

After adding a new file or changing an existing file that needs translations or to add a new language,
edit and run the gen_i18n.py script that is in the scripts/ directory.

```commandline
python scripts/gen_i18n.py
```

After running the script, this directory is populated with new .ts files (if
new languages were added) and the existing .ts files are updated to contain
any new strings that need translation.

Using `linguist`, open the .ts files and add translations for the new languages
and strings (including English, but just click the confirm checkbox).

When done adding translations, run `lrelease brainframe.pro` and the .qm files
will be generated.
