"""This module contains a QGIS plugin to visualize OpenDRIVE maps."""


# noinspection PyPep8Naming
def classFactory(iface):  # noqa: N802
    """Load the OpenDRIVE viewer plugin."""
    #
    from .odrviewer_plugin import OpenDriveViewer

    return OpenDriveViewer(iface)
