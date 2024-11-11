import numpy as np
from qgis.core import QgsFeature
from shapely import LineString

from odrviewer.converter.global_transformer import GlobalTransformer
from odrviewer.geometry import shapely_geometry_to_qgs_geometry
from odrviewer.model.qgis_odr_map import get_reference_line_segments_fields
from odrviewer.pyxodr.road_objects.road import Road
from odrviewer.pyxodr.utils.array import interpolate_path


def convert_reference_line(road: Road, transformer: GlobalTransformer) -> QgsFeature:
    reference_line = transformer.translate_odr_geometry(LineString(road.reference_line))
    ref_line_feature = QgsFeature()
    ref_line_feature.setGeometry(shapely_geometry_to_qgs_geometry(reference_line))
    return ref_line_feature


def convert_reference_line_segments(road: Road, transformer: GlobalTransformer) -> list[QgsFeature]:
    ref_line_segments: list[QgsFeature] = []
    for segment_index, reference_line_geometry_segment in enumerate(road.reference_line_geometries):
        # evaluate the reference line segment geometry
        geometry_coordinates = reference_line_geometry_segment.evaluate_geometry(road.resolution)
        geometry_coordinates = np.array(geometry_coordinates, dtype=object)
        stacked_coordinates = np.vstack(geometry_coordinates).astype(np.float64)
        stacked_coordinates = interpolate_path(stacked_coordinates, resolution=road.resolution)
        reference_line_segment = transformer.translate_odr_geometry(LineString(stacked_coordinates))

        # Create a line segment feature in QGIS.
        ref_line_seg_feature = QgsFeature(get_reference_line_segments_fields())
        ref_line_seg_feature.setAttribute("id", road.id)
        ref_line_seg_feature.setAttribute("segment_index", segment_index)
        ref_line_seg_feature.setAttribute("type", reference_line_geometry_segment.geometry_type.name)
        ref_line_seg_feature.setAttribute("params", str(reference_line_geometry_segment))

        ref_line_seg_feature.setAttribute("heading", reference_line_geometry_segment.heading_offset)
        ref_line_seg_feature.setAttribute("length", reference_line_geometry_segment.length)
        ref_line_seg_feature.setAttribute("xoffset", reference_line_geometry_segment.x_offset)
        ref_line_seg_feature.setAttribute("yoffset", reference_line_geometry_segment.y_offset)
        ref_line_segments.append(ref_line_seg_feature)

        ref_line_seg_feature.setGeometry(shapely_geometry_to_qgs_geometry(reference_line_segment))

    return ref_line_segments
