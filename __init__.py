"""This module contains a QGIS plugin to visualize OpenDRIVE maps."""

import importlib.util
import sys
from pathlib import Path


# noinspection PyPep8Naming
def classFactory(iface):  # noqa: N802
    """Load the OpenDRIVE viewer plugin."""
    required_packages = ["numpy", "scipy", "shapely"]
    for pkg_dependency in required_packages:
        if pkg_dependency in sys.modules or importlib.util.find_spec(pkg_dependency) is not None:
            continue

        raise ImportError(
            f"The dependency {pkg_dependency} for the OpenDRIVE Viewer "
            "is not installed. "
            "There are two ways to resolve this: "
            "(1) install the 'qpip' plugin, restart QGIS, and "
            "re-active the OpenDRIVE Viewer plugin. "
            "(2) manually install the dependencies using: "
            f'"[QGIS_DIR]\\python-qgis.bat -m pip install -r {Path.home()}\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\'
            'default\\python\\plugins\\odrviewer\\requirements.txt"'
        )

    from .odrviewer_plugin import OpenDriveViewer

    return OpenDriveViewer(iface)
