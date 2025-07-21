"""Geometry conversion utility functions."""

from typing import Any

import shapely
from qgis.core import QgsGeometry
from shapely.geometry import LineString
from shapely.geometry.base import BaseGeometry


def np_linestring_to_qgs_geometry(linestring: Any) -> QgsGeometry:
    """Converts a numpy array to QgsGeometry."""
    # The type hint of linestring should be npt.NDArray[np.float64],
    # but the numpy version of QGIS doesn't provide numpy.typing.
    return shapely_geometry_to_qgs_geometry(LineString(linestring))


def shapely_geometry_to_qgs_geometry(shapely_geom: BaseGeometry) -> QgsGeometry:
    """Converts a Shapely geometry to a QgsGeometry.

    It uses wkb (well known binary) as the intermediate conversion step, mainly because QGIS vector layers only support
    WKT/WKB.
    """

    # To address https://github.com/Danaozhong/odrviewer/issues/7, we force the geometries to be 3D.
    # This will add a z dimention for 2D geometries, and will drop all dimensions > 3.
    wkb = shapely.force_3d(shapely_geom).wkb
    geometry = QgsGeometry()
    geometry.fromWkb(wkb)
    return geometry
