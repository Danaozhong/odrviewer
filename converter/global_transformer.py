from dataclasses import dataclass

import shapely.ops
from pyproj import Transformer


@dataclass
class GlobalTransformer:
    # A transformer that transforms coordinates from the EPSG used in the ODR file to WGS-84.
    transformer: Transformer

    # The global offset in x direction, as specified in the ODR file header.
    x_off: float

    # The global offset in y direction, as specified in the ODR file header.
    y_off: float

    # The global offset in z direction, as specified in the ODR file header.
    z_off: float

    def translate_odr_geometry(self, geometry: shapely.Geometry) -> shapely.Geometry:
        """
        Translates a Shapely geometry (e.g. polygon) from a local coordinate system to the
        global WGS-84 coordinate system.
        The translation applies the global x, y and z offsets specified in the header of the
        ODR file, and transforms the coordinates to WGS-84 (if they are not already).

        Returns the translated and transformed coordinates in the WGS-84 coordinate system.
        """
        offset_geometry = shapely.affinity.translate(geometry, self.x_off, self.y_off, self.z_off)
        return shapely.ops.transform(self.transformer.transform, offset_geometry)
