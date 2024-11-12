"""This file contains some test setup to be able to debug the code."""
from pathlib import Path

from odrviewer.converter.convert_odr_to_qgis import load_odr_map


def main_test() -> None:
    """Loads a sample OpenDRIVE file, and checks if the conversion code doesn't crash."""
    load_odr_map(Path(r"./odrviewer/sample_files/Town04.xodr"))


if __name__ == "__main__":
    """Helper `main` when running this file in the debugger."""
    main_test()
