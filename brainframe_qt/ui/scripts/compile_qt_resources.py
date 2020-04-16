import argparse
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from shutil import which

import pyqt5ac

RESOURCE_DIR = Path("resources")
TR_LANGUAGES = ["zh"]

project_root = Path.cwd().resolve()
script_dir = Path(__file__).resolve().parents[1]
assert project_root == script_dir, "Error: Script must be run from root of " \
                                   "client dir"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Compile Qt-related files')
    parser.add_argument('--tr-dev', action='store_true',
                        help="Enabling this flag suppresses exceptions about "
                             "unfinished translations")
    return parser.parse_args()


def main():
    args: argparse.Namespace = parse_args()

    compile_qrc()
    compile_tr(args.tr_dev)


def compile_qrc():
    # noinspection SpellCheckingInspection
    pyqt5ac_config_file = RESOURCE_DIR / "qt_resources.yml"
    pyqt5ac.main(config=str(pyqt5ac_config_file))


def compile_tr(tr_dev: bool = False) -> None:
    print("Updating translation files")

    if not which("pylupdate5"):
        sys.exit("Error: pylupdate5 is not installed. "
                 "Please install pyqt5-dev-tools (if using Ubuntu)")

    i18n_dir = RESOURCE_DIR / "i18n"
    qt_project_file = i18n_dir / "brainframe.pro"

    update_ts_files(i18n_dir, qt_project_file)
    update_qm_files(qt_project_file, tr_dev)


def update_ts_files(i18n_dir: Path, qt_project_file: Path) -> None:
    print("Adding python and ui files to brainframe.pro")

    py_files = sorted(Path.cwd().glob("**/*.py"))
    ui_files = sorted(Path.cwd().glob("**/*.ui"))

    with qt_project_file.open("w+") as pro_fi:
        for py_file in py_files:
            py_file_rel = _relative_path(py_file, i18n_dir)
            pro_fi.write(f"SOURCES += {py_file_rel}\n")

        pro_fi.write("\n")

        for ui_file in ui_files:
            ui_file_rel = _relative_path(ui_file, i18n_dir)
            pro_fi.write(f"FORMS += {ui_file_rel}\n")

        pro_fi.write("\n")

        for language in TR_LANGUAGES:
            pro_fi.write(f"TRANSLATIONS += brainframe_{language}.ts\n")

    # noinspection SpellCheckingInspection
    command = ["pylupdate5", "-verbose", "-noobsolete", str(qt_project_file)]
    output = subprocess.check_output(command, stderr=subprocess.STDOUT) \
        .decode()
    print(output.strip())


def update_qm_files(qt_project_file: Path, tr_dev: bool = False) -> None:
    print("Compiling .qm files")

    output = subprocess.check_output(["lrelease", str(qt_project_file)]) \
        .decode()
    print(output.strip())

    if not tr_dev:
        if re.search(r"[1-9]\d* unfinished", output):
            raise RuntimeError("Error: Not all translations are finished, but "
                               "translation development is not enabled.")


def _relative_path(path1: Path, path2: Path) -> Path:
    # Using os.path.relpath instead of Path.relative_to because it
    # generates ../ paths
    # noinspection PyTypeChecker
    return os.path.relpath(path1, path2)


if __name__ == '__main__':
    main()
