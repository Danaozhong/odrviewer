from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from qgis.core import (
    Qgis,
    QgsCategorizedSymbolRenderer,
    QgsMarkerLineSymbolLayer,
    QgsMarkerSymbol,
    QgsRendererCategory,
    QgsSimpleFillSymbolLayer,
    QgsSimpleLineSymbolLayer,
    QgsSimpleMarkerSymbolLayer,
    QgsSingleSymbolRenderer,
    QgsSymbol,
    QgsVectorLayer,
    QgsWkbTypes,
)

from odrviewer.model.qgis_odr_map import QGISOpenDriveMap


def apply_qgis_styles(odr_map: QGISOpenDriveMap) -> None:
    apply_road_reference_line_style(odr_map.reference_line_segments)
    apply_road_reference_line_style(odr_map.reference_lines)
    apply_road_reference_frame_style(odr_map.reference_frames)
    apply_lane_polygon_style(odr_map.lanes)


def get_default_polygon_symbol_type() -> QgsSymbol:
    return QgsSymbol.defaultSymbol(QgsWkbTypes.geometryType(QgsWkbTypes.Polygon))


def get_default_line_symbol_type() -> QgsSymbol:
    return QgsSymbol.defaultSymbol(QgsWkbTypes.geometryType(QgsWkbTypes.LineString))


def get_default_point_symbol_type() -> QgsSymbol:
    return QgsSymbol.defaultSymbol(QgsWkbTypes.geometryType(QgsWkbTypes.Point))


def apply_road_reference_frame_style(reference_frame_layer: QgsVectorLayer) -> None:
    """
    Applies a custom QGIS style for the reference frame vector layer.
    """

    def get_arrow_style(arrow_color: QColor) -> QgsSymbol:
        symbol = get_default_line_symbol_type()
        # Arrow stem (line)
        line_symbol_layer = QgsSimpleLineSymbolLayer()
        line_symbol_layer.setWidth(0.20000)
        line_symbol_layer.setColor(arrow_color)
        symbol.changeSymbolLayer(0, line_symbol_layer)

        # Arrow tip (small triangle)
        marker_symbol_layer = QgsSimpleMarkerSymbolLayer()
        marker_symbol_layer.setColor(arrow_color)
        marker_symbol_layer.setStrokeColor(arrow_color)
        marker_symbol_layer.setShape(Qgis.MarkerShape.ArrowHeadFilled)
        marker_symbol_layer.setSize(2.0)
        marker_symbol = QgsMarkerSymbol()
        marker_symbol.changeSymbolLayer(0, marker_symbol_layer)

        # Combine both
        marker_layer = QgsMarkerLineSymbolLayer()
        marker_layer.setSubSymbol(marker_symbol)
        marker_layer.setPlacements(Qgis.MarkerLinePlacement.LastVertex)
        symbol.appendSymbolLayer(marker_layer)
        return symbol

    cat_renderer = QgsCategorizedSymbolRenderer("axis")
    cat_renderer.addCategory(QgsRendererCategory("x", get_arrow_style(QColor.fromRgb(255, 0, 0)), "x"))
    cat_renderer.addCategory(QgsRendererCategory("y", get_arrow_style(QColor.fromRgb(0, 255, 0)), "y"))
    reference_frame_layer.setRenderer(cat_renderer)


def apply_road_reference_line_style(reference_line_layer: QgsVectorLayer) -> None:
    """
    Applies a custom QGIS style for the reference line vector layer.
    """

    def get_arrow_style(arrow_color: QColor) -> QgsSymbol:
        symbol = get_default_line_symbol_type()
        # Arrow stem (line)
        line_symbol_layer = QgsSimpleLineSymbolLayer()
        line_symbol_layer.setWidth(0.30000)
        line_symbol_layer.setColor(arrow_color)
        symbol.changeSymbolLayer(0, line_symbol_layer)

        # Arrow tip (small triangle)
        marker_symbol_layer = QgsSimpleMarkerSymbolLayer()
        marker_symbol_layer.setColor(arrow_color)
        marker_symbol_layer.setStrokeColor(arrow_color)
        marker_symbol_layer.setShape(Qgis.MarkerShape.ArrowHeadFilled)
        marker_symbol_layer.setSize(2.0)
        marker_symbol = QgsMarkerSymbol()
        marker_symbol.changeSymbolLayer(0, marker_symbol_layer)

        # Combine both
        marker_layer = QgsMarkerLineSymbolLayer()
        marker_layer.setSubSymbol(marker_symbol)
        marker_layer.setPlacements(Qgis.MarkerLinePlacement.LastVertex)
        symbol.appendSymbolLayer(marker_layer)
        return symbol

    reference_line_layer.setRenderer(QgsSingleSymbolRenderer(get_arrow_style(QColor(50, 50, 50))))


def apply_lane_polygon_style(lane_polygon_layer: QgsVectorLayer) -> None:
    """
    Applies a standardized rendering to the QGIS lane polygon rendering.
    The polygon is colored semi-transparent pink.
    """

    def left_lane_style() -> QgsSymbol:
        symbol = get_default_polygon_symbol_type()
        vector_layer = QgsSimpleFillSymbolLayer()
        vector_layer.setColor(QColor.fromRgb(255, 100, 255, 100))
        vector_layer.setStrokeStyle(Qt.PenStyle.DashLine)
        vector_layer.setStrokeColor(QColor.fromRgb(255, 100, 255, 200))
        symbol.changeSymbolLayer(0, vector_layer)
        return symbol

    def right_lane_style() -> QgsSymbol:
        symbol = get_default_polygon_symbol_type()
        vector_layer = QgsSimpleFillSymbolLayer()
        vector_layer.setColor(QColor.fromRgb(100, 255, 255, 100))
        vector_layer.setStrokeStyle(Qt.PenStyle.DashLine)
        vector_layer.setStrokeColor(QColor.fromRgb(100, 255, 255, 200))
        symbol.changeSymbolLayer(0, vector_layer)
        return symbol

    cat_renderer = QgsCategorizedSymbolRenderer("side")
    cat_renderer.addCategory(QgsRendererCategory("LEFT", left_lane_style(), "LEFT"))
    cat_renderer.addCategory(QgsRendererCategory("RIGHT", right_lane_style(), "RIGHT"))

    lane_polygon_layer.setRenderer(cat_renderer)


def apply_transition_style(transition_layer: QgsVectorLayer) -> None:
    """
    Applies a custom QGIS style for the lane transition vector layer.
    """

    def get_transition_style() -> QgsSymbol:
        lane_color = QColor.fromRgb(200, 0, 0)
        symbol = get_default_line_symbol_type()
        symbol_layer = symbol.symbolLayer(0)
        symbol_layer.setWidth(0.340000)
        symbol_layer.setColor(lane_color)
        symbol.changeSymbolLayer(0, symbol_layer)
        return symbol

    transition_layer.setRenderer(QgsSingleSymbolRenderer(get_transition_style()))
