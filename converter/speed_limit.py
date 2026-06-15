"""Converts an OpenDRIVE lane to a QGIS lane."""


from odrviewer.converter.geometry import gdf_to_linestring
from qgis.core import QgsFeature, QgsMessageLog, Qgis
from shapely import Polygon

from odrviewer.geometry import shapely_geometry_to_qgs_geometry
from odrviewer.model.qgis_odr_map import get_speed_limits_fields
from py_opendrive.model.roads.road import Road
from py_opendrive.evaluator.evaluated_lane_section import EvaluatedLane, EvaluatedLaneSection

def create_speed_limit_features_for_lane(
    road: Road,
    lane_section: EvaluatedLaneSection,
    lane: EvaluatedLane,
) -> list[QgsFeature]:

    assert lane_section.s_properties.s_end is not None, "Lane section s_end must be defined to create speed limit features."
    
    left_boundary_linestring = gdf_to_linestring(lane_section.boundaries[lane.left_boundary_index])
    right_boundary_linestring = gdf_to_linestring(lane_section.boundaries[lane.right_boundary_index])

    speed_limit_features: list[QgsFeature] = []
    for speed_limit_index, speed_limit in enumerate(lane.lane.speed):
        start_s = lane_section.s_properties.s_start + speed_limit.s_offset
        end_s = lane_section.s_properties.s_end
        if speed_limit_index + 1 < len(lane.lane.speed):
            end_s = lane_section.s_properties.s_start + lane.lane.speed[speed_limit_index + 1].s_offset
        
        # Find the geometries for the left and right boundaries.
        start_geom_idx = lane_section.get_geometry_index_at_s(start_s)
        end_geom_idx = lane_section.get_geometry_index_at_s(end_s)
        coords1 = list(left_boundary_linestring.coords[start_geom_idx:end_geom_idx + 1])
        coords2 = list(right_boundary_linestring.coords[start_geom_idx:end_geom_idx + 1])

        # Reverse the second line's coordinates to create a closed loop
        coords2_reversed = coords2[::-1]

        # Concatenate the coordinate lists to form the exterior ring
        polygon_coords = coords1 + coords2_reversed

        # Create the Polygon object
        lane_polygon = Polygon(polygon_coords)


        if lane_polygon.is_empty or not lane_polygon.is_valid:
            QgsMessageLog.logMessage(f"Lane {lane.lane.id} has invalid polygon geometry", level=Qgis.Warning)
            continue
            
        speed_limit_feature = QgsFeature(get_speed_limits_fields())
        speed_limit_feature.setGeometry(shapely_geometry_to_qgs_geometry(lane_polygon))

        speed_limit_feature.setAttribute("road_id", road.id)
        speed_limit_feature.setAttribute("lane_id", lane.lane.id)
        speed_limit_feature.setAttribute("s_offset", speed_limit.s_offset)
        speed_limit_feature.setAttribute("max", speed_limit.max)
        speed_limit_feature.setAttribute("unit", speed_limit.unit.name if speed_limit.unit else "")
        speed_limit_features.append(speed_limit_feature)

    return speed_limit_features
