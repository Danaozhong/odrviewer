from pathlib import Path

from odrviewer.converter.convert_odr_to_qgis import load_odr_map


def main_test() -> None:
    load_odr_map(Path(r"C:\Work\ODR\sample\Town04.xodr"))


if __name__ == "__main__":
    main_test()
