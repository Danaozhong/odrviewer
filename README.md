# odrviewer

A QGIS plugin to visualize OpenDRIVE maps.

To run, extract the Python package to your QGIS Python plug-in directory.

For example, on Windows:
`C:\Users\<user>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`


## Open a Map

Press `Vector` -> `OpenDRIVE Viewer` -> `Open...` to load an OpenDRIVE map into QGIS.

If the OpenDRIVE file provides a valid geo reference in the header, the map will be displayed at the correct location (lat/lon).
Some OpenDRIVE maps don't contain a valid geo reference header (e.g. the official sample files), and these maps will be places "somewhere".

![](img/sample-loaded-in-qgis.png)


## Additional Features

- The plugin creates some additional layers to visualize details of the reference line. This can be helpful when debugging visualization / geometry issues.