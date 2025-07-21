"""The main conversion functions to convert from OpenDRIVE to QGIS."""

from pathlib import Path

from odrviewer.converter.global_transformer import GlobalTransformer
from odrviewer.converter.lane import convert_lanes, convert_road_markings
from odrviewer.converter.reference_frame import convert_reference_frames
from odrviewer.converter.reference_line import convert_reference_line, convert_reference_line_segments
from odrviewer.converter.signal import convert_signals
from odrviewer.model.projections import MERCATOR, WGS84
from odrviewer.model.qgis_odr_map import QGISOpenDriveMap
from odrviewer.pyxodr.road_objects.network import RoadNetwork
from pyproj import CRS, Transformer
from qgis.core import Qgis, QgsFeature, QgsMessageLog


def load_odr_map(odr_filename: Path) -> QGISOpenDriveMap:
    """Loads an OpenDRIVE map from the file system, and converts it to QGIS vector layers."""
    rn = RoadNetwork(str(odr_filename))
    qgis_map = QGISOpenDriveMap()
    qgis_map.initialize_fields()

    # The OpenDRIVE map may use specific coordinate systems. For simplicity we will just
    # convert everything to WGS-84.
    try:
        proj_str = rn.get_geometry_reference()
        from_crs = CRS.from_proj4(proj_str)
    except BaseException:
        # if no proj string is set, or the proj string cannot be parsed, assume Pseudo Mercator projection (meters)
        from_crs = MERCATOR
    try:
        x_off, y_off, z_off, heading_off = rn.get_offset()
    except BaseException:
        # if the offsets are not set, assume them to be 0
        x_off, y_off, z_off, _heading_off = 0, 0, 0, 0

    transformer = GlobalTransformer(
        Transformer.from_crs(crs_from=from_crs, crs_to=WGS84, always_xy=True), x_off, y_off, z_off
    )
    ref_lines: list[QgsFeature] = []
    ref_frames: list[QgsFeature] = []
    ref_line_segments: list[QgsFeature] = []
    lane_polygons: list[QgsFeature] = []
    boundaries: list[QgsFeature] = []
    signals: list[QgsFeature] = []

    # Iterate over all road features in the ODR map, and convert them to QGIS QgsFeatures.
    for road in rn.get_roads():
        ref_line_segments += convert_reference_line_segments(road, transformer)
        ref_frames += convert_reference_frames(road, transformer)
        ref_lines.append(convert_reference_line(road, transformer))
        lane_polygons += convert_lanes(road, transformer)
        boundaries += convert_road_markings(road, transformer)
        signals += convert_signals(road, transformer)

    if not qgis_map.reference_lines.dataProvider().addFeatures(ref_lines):
        QgsMessageLog.logMessage("failed to add reference lines to QGIS map", level=Qgis.Warning)

    if not qgis_map.reference_frames.dataProvider().addFeatures(ref_frames):
        QgsMessageLog.logMessage("failed to add reference frames to QGIS map", level=Qgis.Warning)

    if not qgis_map.reference_line_segments.dataProvider().addFeatures(ref_line_segments):
        QgsMessageLog.logMessage("failed to add reference line segments to QGIS map", level=Qgis.Warning)

    if not qgis_map.lanes.dataProvider().addFeatures(lane_polygons):
        QgsMessageLog.logMessage("failed to add road polygon to QGIS map", level=Qgis.Warning)

    if not qgis_map.boundaries.dataProvider().addFeatures(boundaries):
        QgsMessageLog.logMessage("failed to add boundaries to QGIS map", level=Qgis.Warning)

    if not qgis_map.signals.dataProvider().addFeatures(signals):
        QgsMessageLog.logMessage("failed to add signals to QGIS map", level=Qgis.Warning)

    return qgis_map
