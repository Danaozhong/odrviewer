import numpy as np
import shapely
from qgis.core import QgsFeature
from shapely import Polygon, LineString

from odrviewer.converter.basic_types import LaneSide
from odrviewer.converter.global_transformer import GlobalTransformer
from odrviewer.geometry import shaplely_poygon_to_qgs_geometry
from odrviewer.model.qgis_odr_map import get_lanes_fields, get_boundary_fields
from odrviewer.pyxodr.road_objects.road import Road
import shapely.ops

def create_lane_feature(
    transformer: GlobalTransformer,
    road_id: int,
    lane_id: int,
    side: LaneSide,
    lane_index: int,
    predecessor: list[int],
    successor: list[int],
    inner_boundary,
    outer_boundary,
) -> QgsFeature:
    lane_polygon = Polygon(np.vstack((inner_boundary, np.flip(outer_boundary, axis=0))))
    wgs84_polygon = transformer.translate_odr_geometry(lane_polygon)
    lane_poly_feature = QgsFeature(get_lanes_fields())
    lane_poly_feature.setGeometry(shaplely_poygon_to_qgs_geometry(wgs84_polygon))

    lane_poly_feature.setAttribute("road_id", road_id)
    lane_poly_feature.setAttribute("lane_id", lane_id)
    lane_poly_feature.setAttribute("side", side.name)
    lane_poly_feature.setAttribute("lane_index", lane_index)
    lane_poly_feature.setAttribute("predecessor_ids", ", ".join(str(predecessor)))
    lane_poly_feature.setAttribute("successor_ids", ", ".join(str(successor)))

    return lane_poly_feature


def convert_lanes(road: Road, transformer: GlobalTransformer) -> list[QgsFeature]:
    lane_polygons: list[QgsFeature] = []
    for lane_section in road.lane_sections:
        # start processing the left lanes, if present
        inner_boundary = lane_section.lane_section_offset_line
        for lane_index, lane in enumerate(lane_section.left_lanes):
            outer_boundary = lane.boundary_line

            lane_polygons.append(
                create_lane_feature(
                    transformer=transformer,
                    road_id=road.id,
                    lane_id=lane.id,
                    side=LaneSide.LEFT,
                    lane_index=lane_index,
                    predecessor=lane.predecessor_ids,
                    successor=lane.successor_ids,
                    inner_boundary=inner_boundary,
                    outer_boundary=outer_boundary,
                )
            )
            # the outer boundary is the inner boundary of the next lane
            inner_boundary = outer_boundary

        # process the right lanes, if they exist
        inner_boundary = lane_section.lane_section_offset_line
        for lane_index, lane in enumerate(lane_section.right_lanes):
            outer_boundary = lane.boundary_line

            lane_polygons.append(
                create_lane_feature(
                    transformer=transformer,
                    road_id=road.id,
                    lane_id=lane.id,
                    side=LaneSide.RIGHT,
                    lane_index=lane_index,
                    predecessor=lane.predecessor_ids,
                    successor=lane.successor_ids,
                    inner_boundary=inner_boundary,
                    outer_boundary=outer_boundary,
                )
            )

            inner_boundary = outer_boundary
    return lane_polygons


def convert_road_markings(road: Road, transformer: GlobalTransformer) -> list[QgsFeature]:
    road_markings: list[QgsFeature] = []

    for lane_section in road.lane_sections:
        for lane in lane_section.lanes:
            road_marks = lane.road_marks
            if len(road_marks) == 0:
                continue
            
            s_values = [rm.s_offset for rm in road_marks]
            s_ranges = zip(s_values, s_values[1::] + [None])

        
            for (start_s, end_s), road_mark in zip(s_ranges, road_marks):

                boundary_geometry = lane.get_boundary_line_segment(start_s, end_s)
                if len(boundary_geometry) < 2:
                    # drop segments that are below our pecision accuracy
                    continue
                wgs84_boundary = transformer.translate_odr_geometry(LineString(boundary_geometry))


                lane_poly_feature = QgsFeature(get_boundary_fields())
                lane_poly_feature.setGeometry(shaplely_poygon_to_qgs_geometry(wgs84_boundary))

                lane_poly_feature.setAttribute("road_id", road.id)
                lane_poly_feature.setAttribute("lane_id", lane.id)
                lane_poly_feature.setAttribute("color", road_mark.color)
                lane_poly_feature.setAttribute("height", road_mark.height if road_mark.height is not None else 0.0)
                lane_poly_feature.setAttribute("lane_change", road_mark.lane_change if road_mark.lane_change is not None else "None")
                lane_poly_feature.setAttribute("material", road_mark.material if road_mark.material is not None else "invalid")
                lane_poly_feature.setAttribute("s_offset", road_mark.s_offset)
                lane_poly_feature.setAttribute("type", road_mark.type)
                lane_poly_feature.setAttribute("weight", road_mark.weight if road_mark.weight is not None else 0.0)
                lane_poly_feature.setAttribute("width", road_mark.width if road_mark.width is not None else 0.0)
                road_markings.append(lane_poly_feature)

    return road_markings
