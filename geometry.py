from typing import Any

import numpy as np
from qgis.core import QgsGeometry
from shapely.geometry import LineString, Polygon


def np_linestring_to_qgs_geometry(linestring: Any) -> QgsGeometry:
    """
    Converts a numpy array to QgsGeometry. It uses wkt as the intermediate
    conversion step, mainly because QGIS vector layers only support WKT.
    """
    # The type hint of linestring should be npt.NDArray[np.float64],
    # but the numpy version of QGIS doesn't provide numpy.typing.
    return shapely_linestring_to_qgs_geometry(LineString(linestring))


def shapely_linestring_to_qgs_geometry(linestring: LineString) -> QgsGeometry:
    """
    Converts a Shapely linestring to a QgsGeometry. It uses wkt as the intermediate
    conversion step, mainly because QGIS vector layers only support WKT.
    """
    wkt = linestring.wkt
    return QgsGeometry.fromWkt(wkt)


def shaplely_poygon_to_qgs_geometry(polygon: Polygon) -> QgsGeometry:
    wkt = polygon.wkt
    return QgsGeometry.fromWkt(wkt)
