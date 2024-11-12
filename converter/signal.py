"""Contains the functions to convert OpenDRIVE signals to QGIS."""
import numpy as np
from qgis.core import QgsFeature
from shapely import Point

from odrviewer.converter.global_transformer import GlobalTransformer
from odrviewer.geometry import shapely_geometry_to_qgs_geometry
from odrviewer.model.qgis_odr_map import get_signal_fields
from odrviewer.pyxodr.road_objects.road import Road


def convert_signals(road: Road, transformer: GlobalTransformer) -> list[QgsFeature]:
    """Converts all signals within an OpenDRIVE road to QGS vector layer features."""
    signal_features: list[QgsFeature] = []
    for signal in road.signals:
        # Create a line segment feature in QGIS.
        signal_feature = QgsFeature(get_signal_fields())
        signal_feature.setAttribute("country_revision", signal.country_revision)
        signal_feature.setAttribute("country", signal.country)
        signal_feature.setAttribute("dynamic", signal.dynamic)
        signal_feature.setAttribute("h_offset", signal.h_offset)
        signal_feature.setAttribute("id", signal.id)
        signal_feature.setAttribute("length", signal.length)
        signal_feature.setAttribute("name", signal.name)
        signal_feature.setAttribute("orientation", signal.orientation)
        signal_feature.setAttribute("pitch", signal.pitch)
        signal_feature.setAttribute("roll", signal.roll)
        signal_feature.setAttribute("s", signal.s)
        signal_feature.setAttribute("subtype", signal.subtype)
        signal_feature.setAttribute("t", signal.t)
        signal_feature.setAttribute("type", signal.type)
        signal_feature.setAttribute("text", signal.text)
        signal_feature.setAttribute("width", signal.width)
        signal_feature.setAttribute("z_offset", signal.z_offset)

        # Since not all signs have a valid geometry (i.e. width, height, length set),
        # for now, we only convert the sign center point to a QGIS point feature.

        # We may add different vector layers layer with proper sign polygons.
        position, s_direction = road.get_coordinate_and_direction(signal.s)

        # Get the t direction vector by rotating the s direction vector 90 degrees CCW
        rotation_matrix = np.array([[0, -1], [1, 0]])
        direction_vector = np.dot(rotation_matrix, s_direction)

        t_direction = np.linalg.norm(direction_vector)
        # transform to WGS-84
        shapely_position = transformer.translate_odr_geometry(Point(position + signal.t * t_direction))
        signal_feature.setGeometry(shapely_geometry_to_qgs_geometry(shapely_position))
        signal_features.append(signal_feature)

    return signal_features
