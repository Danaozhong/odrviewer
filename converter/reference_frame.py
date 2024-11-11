import numpy as np
from qgis.core import QgsFeature
from shapely import LineString

from odrviewer.converter.global_transformer import GlobalTransformer
from odrviewer.geometry import shapely_geometry_to_qgs_geometry
from odrviewer.model.qgis_odr_map import get_reference_frame_fields
from odrviewer.pyxodr.geometries.base import Geometry
from odrviewer.pyxodr.road_objects.road import Road
from odrviewer.pyxodr.utils.array import interpolate_path


def get_axis(
    transformer: GlobalTransformer, road_id: str, segment_index: int, reference_geometry: Geometry, axis_label: str
) -> QgsFeature:
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
    ref_line_segments: list[QgsFeature] = []
    for segment_index, reference_line_geometry_segment in enumerate(road.reference_line_geometries):
        ref_line_segments += [
            get_axis(transformer, road.id, segment_index, reference_line_geometry_segment, "x"),
            get_axis(transformer, road.id, segment_index, reference_line_geometry_segment, "y"),
        ]

    return ref_line_segments
