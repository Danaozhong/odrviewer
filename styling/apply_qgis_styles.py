"""Apply QGIS rendering styles for the OpenDRIVE map."""

from odrviewer.model.qgis_odr_map import QGISOpenDriveMap
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from qgis.core import (Qgis, QgsCategorizedSymbolRenderer, QgsMarkerLineSymbolLayer, QgsMarkerSymbol,
                       QgsRendererCategory, QgsRuleBasedRenderer, QgsSimpleFillSymbolLayer, QgsSimpleLineSymbolLayer,
                       QgsSimpleMarkerSymbolLayer, QgsSingleSymbolRenderer, QgsSymbol, QgsVectorLayer, QgsWkbTypes)


def apply_qgis_styles(odr_map: QGISOpenDriveMap) -> None:
    """Applies custom rendering configurations to the QGIS map layers.

    Each layer receives a custom rendering to make inspection
    more intuitive, such as pre-categorizing traffic signal types,
    or boundary types (e.g. dashed white line).
    """
    apply_road_reference_line_style(odr_map.reference_line_segments)
    apply_road_reference_line_style(odr_map.reference_lines)
    apply_road_reference_frame_style(odr_map.reference_frames)
    apply_lane_polygon_style(odr_map.lanes)
    apply_boundary_style(odr_map.boundaries)
    apply_signal_layer_style(odr_map.signals)


def get_default_polygon_symbol_type() -> QgsSymbol:
    """Returns the default QGIS symbol type for a polygon."""
    return QgsSymbol.defaultSymbol(QgsWkbTypes.geometryType(QgsWkbTypes.Polygon))


def get_default_line_symbol_type() -> QgsSymbol:
    """Returns the default QGIS symbol type for a line."""
    return QgsSymbol.defaultSymbol(QgsWkbTypes.geometryType(QgsWkbTypes.LineString))


def get_default_point_symbol_type() -> QgsSymbol:
    """Returns the default QGIS symbol type for a point."""
    return QgsSymbol.defaultSymbol(QgsWkbTypes.geometryType(QgsWkbTypes.Point))


def apply_road_reference_frame_style(reference_frame_layer: QgsVectorLayer) -> None:
    """Applies a custom QGIS style for the reference frame vector layer."""

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
    """Applies a custom QGIS style for the reference line vector layer."""

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
    """Applies a standardized rendering to the QGIS lane polygon rendering."""

    def left_lane_style() -> QgsSymbol:
        symbol = get_default_polygon_symbol_type()
        vector_layer = QgsSimpleFillSymbolLayer()
        vector_layer.setColor(QColor.fromRgb(255, 100, 255, 50))
        vector_layer.setStrokeStyle(Qt.PenStyle.DashLine)
        vector_layer.setStrokeColor(QColor.fromRgb(255, 100, 255, 80))
        symbol.changeSymbolLayer(0, vector_layer)
        return symbol

    def right_lane_style() -> QgsSymbol:
        symbol = get_default_polygon_symbol_type()
        vector_layer = QgsSimpleFillSymbolLayer()
        vector_layer.setColor(QColor.fromRgb(100, 255, 255, 50))
        vector_layer.setStrokeStyle(Qt.PenStyle.DashLine)
        vector_layer.setStrokeColor(QColor.fromRgb(100, 255, 255, 80))
        symbol.changeSymbolLayer(0, vector_layer)
        return symbol

    cat_renderer = QgsCategorizedSymbolRenderer("side")
    cat_renderer.addCategory(QgsRendererCategory("LEFT", left_lane_style(), "LEFT"))
    cat_renderer.addCategory(QgsRendererCategory("RIGHT", right_lane_style(), "RIGHT"))

    lane_polygon_layer.setRenderer(cat_renderer)


def apply_transition_style(transition_layer: QgsVectorLayer) -> None:
    """Applies a custom QGIS style for the lane transition vector layer."""

    def get_transition_style() -> QgsSymbol:
        lane_color = QColor.fromRgb(200, 0, 0)
        symbol = get_default_line_symbol_type()
        symbol_layer = symbol.symbolLayer(0)
        symbol_layer.setWidth(0.340000)
        symbol_layer.setColor(lane_color)
        symbol.changeSymbolLayer(0, symbol_layer)
        return symbol

    transition_layer.setRenderer(QgsSingleSymbolRenderer(get_transition_style()))


def apply_boundary_style(boundary_layer: QgsVectorLayer) -> None:
    """Apply QGIS styling for the boundary geometries."""

    def unknown_sym() -> QgsSymbol:
        symbol = get_default_line_symbol_type()
        symbol_layer = QgsSimpleLineSymbolLayer()
        symbol_layer.setWidth(0.44)
        symbol_layer.setColor(QColor.fromRgb(200, 200, 200))
        symbol.changeSymbolLayer(0, symbol_layer)
        return symbol

    def logical_sym() -> QgsSymbol:
        symbol = get_default_line_symbol_type()
        symbol_layer = QgsSimpleLineSymbolLayer()
        symbol_layer.setWidth(0.44)
        symbol_layer.setColor(QColor.fromRgb(255, 0, 255))
        symbol_layer.setPenStyle(Qt.PenStyle.DotLine)
        symbol.changeSymbolLayer(0, symbol_layer)
        return symbol

    def painted_boundary_sym(color: QColor, dashed: bool) -> QgsSymbol:
        symbol = get_default_line_symbol_type()
        line_marker = QgsSimpleLineSymbolLayer()
        line_marker.setWidth(0.44)
        line_marker.setColor(color)
        if dashed:
            line_marker.setPenStyle(Qt.PenStyle.DashLine)
        symbol.changeSymbolLayer(0, line_marker)
        return symbol

    def physical_divider_sym() -> QgsSymbol:
        symbol = get_default_line_symbol_type()
        line_marker = QgsSimpleLineSymbolLayer()
        line_marker.setWidth(0.66)
        line_marker.setColor(QColor.fromRgb(255, 0, 0))
        symbol.changeSymbolLayer(0, line_marker)
        return symbol

    yellow = QColor.fromRgb(255, 200, 10)
    white = QColor.fromRgb(128, 128, 128)

    # set the color of the road based on if the road is part of an intersection.
    root_rule = QgsRuleBasedRenderer.Rule(None)
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            painted_boundary_sym(white, True),
            0,
            0,
            "type is 'broken' and color is 'white'",
            "Dashed White Line",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            painted_boundary_sym(yellow, True),
            0,
            0,
            "type is 'broken' and color is 'yellow'",
            "Dashed Yellow Line",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            painted_boundary_sym(white, False),
            0,
            0,
            "type is 'solid' and color is 'white'",
            "Solid White Line",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            painted_boundary_sym(yellow, False),
            0,
            0,
            "type is 'solid' and color is 'yellow'",
            "Solid Yellow Line",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            physical_divider_sym(),
            0,
            0,
            "type is 'curb'",
            "Curb",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            logical_sym(),
            0,
            0,
            "type is 'none'",
            "Logical",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            unknown_sym(),
            0,
            0,
            "ELSE",
            "OTHER",
        )
    )

    cat_renderer = QgsRuleBasedRenderer(root_rule)
    boundary_layer.setRenderer(cat_renderer)
    boundary_layer.triggerRepaint()


def apply_signal_layer_style(signal_point_layer: QgsVectorLayer) -> None:
    """Applies a standardized rendering to the QGIS signal layer."""

    def get_speed_limit_sign_style() -> QgsSymbol:
        symbol = get_default_point_symbol_type()
        symbol_marker = QgsSimpleMarkerSymbolLayer()
        symbol_marker.setShape(Qgis.MarkerShape.Square)
        symbol_marker.setColor(QColor.fromRgb(255, 255, 255))
        symbol_marker.setSize(2.0)
        symbol.changeSymbolLayer(0, symbol_marker)
        return symbol

    def get_yield_sign_style() -> QgsSymbol:
        symbol = get_default_point_symbol_type()
        symbol_marker = QgsSimpleMarkerSymbolLayer()
        symbol_marker.setShape(Qgis.MarkerShape.Triangle)
        symbol_marker.setAngle(180.0)
        symbol_marker.setSize(2.0)
        symbol.changeSymbolLayer(0, symbol_marker)
        return symbol

    def get_stop_sign_style() -> QgsSymbol:
        symbol = get_default_point_symbol_type()
        symbol_marker = QgsSimpleMarkerSymbolLayer()
        symbol_marker.setColor(QColor.fromRgb(255, 0, 0))
        symbol_marker.setShape(Qgis.MarkerShape.Octagon)
        symbol_marker.setSize(2.0)
        symbol.changeSymbolLayer(0, symbol_marker)
        return symbol

    def get_traffic_light() -> QgsSymbol:
        symbol = get_default_point_symbol_type()
        symbol_marker = QgsSimpleMarkerSymbolLayer()
        symbol_marker.setShape(Qgis.MarkerShape.Circle)
        symbol_marker.setColor(QColor.fromRgb(255, 0, 0))
        symbol_marker.setSize(2.0)
        symbol.changeSymbolLayer(0, symbol_marker)
        return symbol

    def get_pedestrian_crossing_sign() -> QgsSymbol:
        symbol = get_default_point_symbol_type()
        symbol_marker = QgsSimpleMarkerSymbolLayer()
        symbol_marker.setShape(Qgis.MarkerShape.Circle)
        symbol_marker.setColor(QColor.fromRgb(255, 155, 20))
        symbol_marker.setAngle(180.0)
        symbol_marker.setSize(2.0)
        symbol.changeSymbolLayer(0, symbol_marker)
        return symbol

    def get_other_sign_style() -> QgsSymbol:
        symbol = get_default_point_symbol_type()
        symbol_marker = QgsSimpleMarkerSymbolLayer()
        symbol_marker.setColor(QColor.fromRgb(100, 100, 100))
        symbol_marker.setSize(2.0)
        symbol.changeSymbolLayer(0, symbol_marker)
        return symbol

    # TODO - right now, this uses the German standard for signs.
    # Eventually, the country code should be evaluated as well.

    root_rule = QgsRuleBasedRenderer.Rule(None)
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            get_pedestrian_crossing_sign(),
            0,
            0,
            "(country is 'US' and type is 'R9-8') or (country is 'DE' and type is '101-11')",
            "Pedestrian Crossing Sign",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            get_traffic_light(),
            0,
            0,
            "country is 'OpenDRIVE' and type is '1000001'",
            "Traffic Light (3 bulb vertical)",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            get_traffic_light(),
            0,
            0,
            "country is 'OpenDRIVE' and type is '1000009'",
            "Traffic Light (2 bulb vertical)",
        )
    )

    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            get_speed_limit_sign_style(),
            0,
            0,
            "country is 'US' and type is 'R2-1'",
            "Speed Limit Sign (50mph)",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            get_yield_sign_style(),
            0,
            0,
            "(country is 'US' and type is 'R1-2') or (country is 'DE' and type is '205')",
            "Yield Sign",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            get_stop_sign_style(),
            0,
            0,
            "(country is 'US' and type is 'R1-1') or (country is 'DE' and type is '206')",
            "Stop Sign",
        )
    )
    root_rule.appendChild(
        QgsRuleBasedRenderer.Rule(
            get_other_sign_style(),
            0,
            0,
            "ELSE",
            "Other",
        )
    )

    cat_renderer = QgsRuleBasedRenderer(root_rule)
    signal_point_layer.setRenderer(cat_renderer)
