"""Converts an OpenDRIVE reference frame into a QGIS visualization.

The reference frame is visualized by drawing an arrow of length=1 in x and y direction,
originating from the origin.
This is used to simplify debugging and better understanding the OpenDRIVE geometry encoding.
"""

import numpy as np
from odrviewer.converter.global_transformer import GlobalTransformer
from odrviewer.geometry import shapely_geometry_to_qgs_geometry
from odrviewer.model.qgis_odr_map import get_reference_frame_fields
from odrviewer.pyxodr.geometries.base import Geometry
from odrviewer.pyxodr.road_objects.road import Road
from qgis.core import QgsFeature
from shapely import LineString


def get_axis(
    transformer: GlobalTransformer, road_id: str, segment_index: int, reference_geometry: Geometry, axis_label: str
) -> QgsFeature:
    """Returns either the X or Y axis of a frame visualization."""
    num_samples = 2
    # Construct direction vector directly from the heading (in radians)
    if axis_label.lower() == "x":
        direction_vector = np.array(
            [np.cos(reference_geometry.heading_offset), np.sin(reference_geometry.heading_offset)]
        )
    else:
        direction_vector = np.array(
            [-np.sin(reference_geometry.heading_offset), np.cos(reference_geometry.heading_offset)]
        )
    # Note this direction vector is normalized by construction
    origin_coordinates_tensor = np.tile(
        np.array([reference_geometry.x_offset, reference_geometry.y_offset]), (num_samples, 1)
    )
    direction_tensor = np.tile(direction_vector, (num_samples, 1))

    line_coordinates = origin_coordinates_tensor + (direction_tensor.T * np.linspace(0, 1, num_samples)).T
    final_coordinates = transformer.translate_odr_geometry(LineString(line_coordinates))

    # Create a line segment feature in QGIS.
    ref_frame_feature = QgsFeature(get_reference_frame_fields())
    ref_frame_feature.setAttribute("id", road_id)
    ref_frame_feature.setAttribute("segment_index", segment_index)
    ref_frame_feature.setAttribute("axis", axis_label)

    ref_frame_feature.setAttribute("heading", reference_geometry.heading_offset)
    ref_frame_feature.setAttribute("xoffset", reference_geometry.x_offset)
    ref_frame_feature.setAttribute("yoffset", reference_geometry.y_offset)
    ref_frame_feature.setGeometry(shapely_geometry_to_qgs_geometry(LineString(final_coordinates)))
    return ref_frame_feature


def convert_reference_frames(road: Road, transformer: GlobalTransformer) -> list[QgsFeature]:
    """Takes all reference frames from the road reference line, and converts them to QGIS features."""
    ref_line_segments: list[QgsFeature] = []
    for segment_index, reference_line_geometry_segment in enumerate(road.reference_line_geometries):
        ref_line_segments += [
            get_axis(transformer, road.id, segment_index, reference_line_geometry_segment, "x"),
            get_axis(transformer, road.id, segment_index, reference_line_geometry_segment, "y"),
        ]

    return ref_line_segments
