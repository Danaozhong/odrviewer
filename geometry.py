from typing import Any

import numpy as np
from qgis.core import QgsGeometry
from shapely.geometry import LineString
from shapely.geometry.base import BaseGeometry


def np_linestring_to_qgs_geometry(linestring: Any) -> QgsGeometry:
    """
    Converts a numpy array to QgsGeometry. It uses wkt as the intermediate
    conversion step, mainly because QGIS vector layers only support WKT.
    """
    # The type hint of linestring should be npt.NDArray[np.float64],
    # but the numpy version of QGIS doesn't provide numpy.typing.
    return shapely_geometry_to_qgs_geometry(LineString(linestring))


def shapely_geometry_to_qgs_geometry(shapely_geom: BaseGeometry) -> QgsGeometry:
    """
    Converts a Shapely geometry to a QgsGeometry. It uses wkt as the intermediate
    conversion step, mainly because QGIS vector layers only support WKT.
    """
    wkt = shapely_geom.wkt
    return QgsGeometry.fromWkt(wkt)
