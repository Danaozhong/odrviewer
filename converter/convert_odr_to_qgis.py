"""The main conversion functions to convert from OpenDRIVE to QGIS."""

from pathlib import Path

from odrviewer.converter.reference_line import convert_reference_line, convert_reference_line_segments
from odrviewer.model.qgis_odr_map import QGISOpenDriveMap
from odrviewer.converter.lane import convert_lanes
from py_opendrive.evaluator.evaluate_opendrive import evaluate_open_drive
from py_opendrive.evaluator.evaluation_properties import EvaluationProperties
from py_opendrive.io.reader import read_file
from qgis.core import Qgis, QgsFeature, QgsMessageLog


def load_odr_map(odr_filename: Path) -> QGISOpenDriveMap:
    """Loads an OpenDRIVE map from the file system, and converts it to QGIS vector layers."""
    odr_map = read_file(str(odr_filename))
    qgis_map = QGISOpenDriveMap()
    qgis_map.initialize_fields()

    # Interpolate the OpenDRIVE geometries as linestrings.
    evaluation_properties = EvaluationProperties(
        shape_points_per_meter=0.2,
        override_crs="EPSG:4326",
    )


    evaluated_odr_map = evaluate_open_drive(odr_map, evaluation_properties)


    ref_lines: list[QgsFeature] = []
    ref_frames: list[QgsFeature] = []
    ref_line_segments: list[QgsFeature] = []
    boundaries: list[QgsFeature] = []
    signals: list[QgsFeature] = []

    # Iterate over all road features in the ODR map, and convert them to QGIS QgsFeatures.
    for road in evaluated_odr_map.evaluated_roads:
        ref_line_segments += convert_reference_line_segments(road)
        #ref_frames += convert_reference_frames(road)
        ref_lines.append(convert_reference_line(road))
        convert_lanes(road, qgis_map)
        #boundaries += convert_road_markings(road)
        #signals += convert_signals(road)

    if not qgis_map.reference_lines.dataProvider().addFeatures(ref_lines):
        QgsMessageLog.logMessage("failed to add reference lines to QGIS map", level=Qgis.Warning)

    if not qgis_map.reference_frames.dataProvider().addFeatures(ref_frames):
        QgsMessageLog.logMessage("failed to add reference frames to QGIS map", level=Qgis.Warning)

    if not qgis_map.reference_line_segments.dataProvider().addFeatures(ref_line_segments):
        QgsMessageLog.logMessage("failed to add reference line segments to QGIS map", level=Qgis.Warning)


    if not qgis_map.boundaries.dataProvider().addFeatures(boundaries):
        QgsMessageLog.logMessage("failed to add boundaries to QGIS map", level=Qgis.Warning)

    if not qgis_map.signals.dataProvider().addFeatures(signals):
        QgsMessageLog.logMessage("failed to add signals to QGIS map", level=Qgis.Warning)

    return qgis_map
