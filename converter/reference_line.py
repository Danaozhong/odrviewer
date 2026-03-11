"""Conversion functions to convert road reference lines to QGIS linestring features."""

from odrviewer.converter.geometry import gdf_to_linestring
from odrviewer.geometry import shapely_geometry_to_qgs_geometry
from odrviewer.model.qgis_odr_map import get_reference_line_segments_fields
from py_opendrive.evaluator.evaluated_lane_section import EvaluatedRoad
from qgis.core import QgsFeature


def convert_reference_line(road: EvaluatedRoad) -> QgsFeature:
    """Converts the reference line within an OpenDRIVE road to a QGS vector layer feature."""
    ref_line_feature = QgsFeature()
    ref_line_feature.setGeometry(shapely_geometry_to_qgs_geometry(gdf_to_linestring(road.evaluated_reference_line)))
    return ref_line_feature


def convert_reference_line_segments(road: EvaluatedRoad) -> list[QgsFeature]:
    """Converts all reference line geometry segments within an OpenDRIVE road to QGS vector layer features."""
    ref_line_segments: list[QgsFeature] = []
    for lane_section_index, lane_section in enumerate(road.evaluated_lane_sections):
        for _, reference_line_geometry_segment in lane_section.reference_line_geometry.iterrows():
            # evaluate the reference line segment geometry

            # Create a line segment feature in QGIS.
            ref_line_seg_feature = QgsFeature(get_reference_line_segments_fields())
            ref_line_seg_feature.setAttribute("id", road.road.id)
            ref_line_seg_feature.setAttribute("geometry_segment_index", reference_line_geometry_segment["geometry_index"])
            ref_line_seg_feature.setAttribute("lane_section_index", lane_section_index)
            ref_line_seg_feature.setAttribute("type", reference_line_geometry_segment["geometry_type"])
            ref_line_seg_feature.setAttribute("p", reference_line_geometry_segment["p"])
            ref_line_seg_feature.setAttribute("s", reference_line_geometry_segment["s"])

            geometry_element = road.road.plan_view.geometries[int(reference_line_geometry_segment["geometry_index"])]

            ref_line_seg_feature.setAttribute("params", str(geometry_element))

            ref_line_seg_feature.setAttribute("heading", geometry_element.hdg)
            ref_line_seg_feature.setAttribute("length", geometry_element.length)
            ref_line_seg_feature.setAttribute("xoffset", geometry_element.x)
            ref_line_seg_feature.setAttribute("yoffset", geometry_element.y)
            ref_line_seg_feature.setGeometry(shapely_geometry_to_qgs_geometry(reference_line_geometry_segment.geometry))
            ref_line_segments.append(ref_line_seg_feature)

    return ref_line_segments
