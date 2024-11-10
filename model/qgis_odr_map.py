from dataclasses import dataclass, field

from PyQt5.QtCore import QVariant
from qgis.core import QgsField, QgsFields, QgsVectorLayer


@dataclass
class QGISOpenDriveMap:
    """
    A dataclass storing an OpenDRIVE map, encoded as QGIS vector layers.
    """

    # All reference lines
    reference_lines: QgsVectorLayer = field(
        default_factory=lambda: QgsVectorLayer("LineString?crs=EPSG:4326", "reference_lines", "memory")
    )

    # All reference line geometry segments
    reference_line_segments: QgsVectorLayer = field(
        default_factory=lambda: QgsVectorLayer("LineString?crs=EPSG:4326", "reference_line_segments", "memory")
    )

    # The reference frames.
    reference_frames: QgsVectorLayer = field(
        default_factory=lambda: QgsVectorLayer("LineString?crs=EPSG:4326", "reference_frames", "memory")
    )

    # The lane polygons.
    lanes: QgsVectorLayer = field(default_factory=lambda: QgsVectorLayer("Polygon?crs=EPSG:4326", "lanes", "memory"))

    # Lane lines / boundaries
    boundaries: QgsVectorLayer = field(default_factory=lambda: QgsVectorLayer("LineString?crs=EPSG:4326", "boundaries", "memory"))

    def initialize_fields(self) -> None:
        """
        This function initializes all the data fields of each feature.
        """
        # initialize_fields(self.reference_lines, get_reference_lines_fields())
        initialize_fields(self.lanes, get_lanes_fields())
        initialize_fields(self.reference_line_segments, get_reference_line_segments_fields())
        initialize_fields(self.reference_frames, get_reference_frame_fields())
        initialize_fields(self.boundaries, get_boundary_fields())


def initialize_fields(qgs_layer: QgsVectorLayer, fields: QgsFields) -> None:
    data_provider = qgs_layer.dataProvider()
    qgs_layer.startEditing()
    data_provider.addAttributes(fields)
    qgs_layer.commitChanges()


def get_reference_lines_fields() -> QgsFields:
    fields = QgsFields()
    fields.append(QgsField("id", QVariant.String))
    return fields


def get_reference_line_segments_fields() -> QgsFields:
    fields = QgsFields()
    fields.append(QgsField("id", QVariant.String))
    fields.append(QgsField("segment_index", QVariant.Int))
    fields.append(QgsField("type", QVariant.String))
    fields.append(QgsField("params", QVariant.String))
    fields.append(QgsField("length", QVariant.Double))
    fields.append(QgsField("heading", QVariant.Double))
    fields.append(QgsField("xoffset", QVariant.Double))
    fields.append(QgsField("yoffset", QVariant.Double))
    return fields


def get_reference_frame_fields() -> QgsFields:
    fields = QgsFields()
    fields.append(QgsField("id", QVariant.String))
    fields.append(QgsField("segment_index", QVariant.Int))
    fields.append(QgsField("axis", QVariant.String))
    fields.append(QgsField("heading", QVariant.Double))
    fields.append(QgsField("xoffset", QVariant.Double))
    fields.append(QgsField("yoffset", QVariant.Double))
    return fields


def get_lanes_fields() -> QgsFields:
    fields = QgsFields()
    fields.append(QgsField("road_id", QVariant.String))
    fields.append(QgsField("lane_id", QVariant.Int))
    fields.append(QgsField("lane_index", QVariant.String))
    fields.append(QgsField("side", QVariant.String))
    fields.append(QgsField("predecessor_ids", QVariant.String))
    fields.append(QgsField("successor_ids", QVariant.String))
    return fields

def get_boundary_fields() -> QgsFields:
    fields = QgsFields()
    fields.append(QgsField("road_id", QVariant.String))
    fields.append(QgsField("lane_id", QVariant.Int))
    fields.append(QgsField("color", QVariant.String))
    fields.append(QgsField("height", QVariant.Double))
    fields.append(QgsField("lane_change", QVariant.String))
    fields.append(QgsField("material", QVariant.String))
    fields.append(QgsField("s_offset", QVariant.Double))
    fields.append(QgsField("type", QVariant.String))
    fields.append(QgsField("weight", QVariant.Double))
    fields.append(QgsField("width", QVariant.Double))
    

    return fields
