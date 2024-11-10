import numpy as np
import shapely
from qgis.core import QgsFeature
from shapely import Polygon

from odrviewer.converter.basic_types import LaneSide
from odrviewer.converter.global_transformer import GlobalTransformer
from odrviewer.geometry import shaplely_poygon_to_qgs_geometry
from odrviewer.model.qgis_odr_map import get_lanes_fields
from odrviewer.pyxodr.road_objects.road import Road


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
