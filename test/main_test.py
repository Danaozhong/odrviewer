"""This file contains some test setup to be able to debug the code."""
from pathlib import Path

from odrviewer.converter.convert_odr_to_qgis import load_odr_map

FIXTURE_DIR = Path(__file__).parent.parent.resolve()


def test_loading_sample_odr_file():
    """This test case loads a sample OpenDRIVE map."""
    load_odr_map(FIXTURE_DIR / "sample_files" / "Town04.xodr")


if __name__ == "__main__":
    """Helper `main` when running this file in the debugger."""
    load_odr_map(Path(r"./odrviewer/sample_files/Town04.xodr"))
