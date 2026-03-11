from shapely import LineString
import geopandas as gpd
import shapely

def gdf_to_linestring(gdf: gpd.GeoDataFrame) -> LineString:
    """Converts a GeoDataFrame with line geometry to a Shapely LineString."""
    points = []
    for _, row in gdf.sort_values("s").iterrows():
        points.append(row.geometry)
    return shapely.LineString(points)


def multipoint_to_linestring(multipoint: shapely.MultiPoint) -> LineString:
    """Converts a shapely multipoint geometry with line geometry to a Shapely LineString."""
    points = [geom.coords[0] for geom in multipoint.geoms]
    return LineString(points)