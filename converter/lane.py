"""Converts an OpenDRIVE lane to a QGIS lane."""


from typing import Optional
from odrviewer.converter.geometry import gdf_to_linestring
from qgis.core import QgsFeature, QgsMessageLog, Qgis
from shapely import Polygon

from odrviewer.converter.basic_types import LaneSide
from odrviewer.geometry import shapely_geometry_to_qgs_geometry
from odrviewer.model.qgis_odr_map import get_lanes_fields
from py_opendrive.model.roads.road import Road
from py_opendrive.evaluator.evaluated_lane_section import EvaluatedLane, EvaluatedLaneSection, EvaluatedRoad
from odrviewer.model.qgis_odr_map import QGISOpenDriveMap
from odrviewer.converter.speed_limit import create_speed_limit_features_for_lane

def create_lane_feature(
    road: Road,
    lane_section: EvaluatedLaneSection,
    lane_section_idx: int,
    lane: EvaluatedLane,
    side: LaneSide,
    lane_index: int,
    predecessor: list[int],
    successor: list[int],
) -> Optional[QgsFeature]:
    """Creates a QGIS vector layer feature from an OpenDRIVE lane."""
    left_boundary_linestring = gdf_to_linestring(lane_section.boundaries[lane.left_boundary_index])
    right_boundary_linestring = gdf_to_linestring(lane_section.boundaries[lane.right_boundary_index])

    # 2. Extract coordinates
    coords1 = list(left_boundary_linestring.coords)
    coords2 = list(right_boundary_linestring.coords)

    # 3. Reverse the second line's coordinates to create a closed loop
    coords2_reversed = coords2[::-1]

    # 4. Concatenate the coordinate lists to form the exterior ring
    polygon_coords = coords1 + coords2_reversed

    # 5. Create the Polygon object
    # The constructor automatically closes the ring by connecting the last point to the first.
    lane_polygon = Polygon(polygon_coords)


    if lane_polygon.is_empty or not lane_polygon.is_valid:
        QgsMessageLog.logMessage(f"Lane {lane.lane.id} has invalid polygon geometry", level=Qgis.Warning)
        return None
    lane_poly_feature = QgsFeature(get_lanes_fields())
    lane_poly_feature.setGeometry(shapely_geometry_to_qgs_geometry(lane_polygon))

    lane_poly_feature.setAttribute("road_id", road.id)
    lane_poly_feature.setAttribute("junction", road.junction)
    lane_poly_feature.setAttribute("road_name", road.name)
    lane_poly_feature.setAttribute("road_length", road.length)
    lane_poly_feature.setAttribute("road_rule", road.rule.name if road.rule else "")
    lane_poly_feature.setAttribute("lane_section_idx", lane_section_idx)
    lane_poly_feature.setAttribute("lane_id", lane.lane.id)
    lane_poly_feature.setAttribute("lane_type", lane.lane.type.name)
    lane_poly_feature.setAttribute("side", side.name)
    lane_poly_feature.setAttribute("lane_index", lane_index)
    lane_poly_feature.setAttribute("predecessor_ids", "")
    lane_poly_feature.setAttribute("successor_ids", "")

    return lane_poly_feature


def convert_lanes(road: EvaluatedRoad, qgis_map: QGISOpenDriveMap) -> None:
    """Converts all lanes of a OpenDRIVE road."""

    if road.road.id == "684" and road.road.junction == "669":
        print("T")
    lane_polygons: list[QgsFeature] = []
    speed_limit_features: list[QgsFeature] = []
    for lane_section_idx, lane_section in enumerate(road.evaluated_lane_sections):
        # start processing the left lanes, if present
        lanes: list[tuple[LaneSide, list[EvaluatedLane]]] = [(LaneSide.LEFT, lane_section.left_lanes), (LaneSide.RIGHT, lane_section.right_lanes)]
        for side, lane_list in lanes:
            for lane_index, lane in enumerate(lane_list):
                lane_feature = create_lane_feature(
                        road=road.road,
                        lane_section=lane_section,
                        lane_section_idx=lane_section_idx,
                        lane=lane,
                        side=side,
                        lane_index=lane_index,
                        predecessor=[],
                        successor=[],
                    )
                # The conversion can fail, for example if the geometry is invalid.
                if lane_feature:
                    lane_polygons.append(lane_feature)

                speed_limit_features += create_speed_limit_features_for_lane(
                    road=road.road,
                    lane_section=lane_section,
                    lane=lane,
                )

    if len(speed_limit_features) > 0:
        if not qgis_map.speed_limits.dataProvider().addFeatures(speed_limit_features):
            QgsMessageLog.logMessage("failed to add speed limit features to QGIS map", level=Qgis.Warning)
        
    if not qgis_map.lanes.dataProvider().addFeatures(lane_polygons):
        QgsMessageLog.logMessage("failed to add road polygon to QGIS map", level=Qgis.Warning)

