# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load the OpenDRIVE viewer plugin."""
    #
    from .odrviewer_plugin import OpenDriveViewer

    return OpenDriveViewer(iface)
