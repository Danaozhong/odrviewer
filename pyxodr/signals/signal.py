from dataclasses import dataclass
from typing import Optional
from odrviewer.pyxodr.enumerations import CountryCode, Orientation, Unit
from lxml.etree import _Element


@dataclass
class Signal:
    country_revision: Optional[str]
    country: Optional[CountryCode]
    dynamic: bool
    h_offset: Optional[float]
    height: Optional[float]
    id: str
    length: Optional[float]
    name: Optional[str]
    orientation: Orientation
    pitch: Optional[float]
    roll: Optional[float]
    s: float
    subtype: str
    t: float
    text: Optional[str]
    type: str
    unit: Optional[Unit]
    value: Optional[float]
    width: Optional[float]
    z_offset: float

    def from_xml_node(node: _Element) -> "Signal":
        return Signal(
            country_revision=node.get("countryRevision", None),
            country=node.get("country", None),
            dynamic=node.get("dynamic", False),
            h_offset=node.get("hOffset", None),
            height=node.get("height", None),
            id=node.get("id", "invalid_id"),
            length=node.get("length", None),
            name=node.get("name", None),
            orientation=node.get("orientation", None),
            pitch=node.get("pitch", None),
            roll=node.get("roll", None),
            s=float(node.get("s", 0.0)),
            subtype=node.get("subtype", ""),
            t=float(node.get("t", 0.0)),
            text=node.get("text", None),
            type=node.get("type", "none"),
            unit=node.get("unit", None),
            value=node.get("value", None),
            width=node.get("width", None),
            z_offset=float(node.get("zOffset", 0.0)),
        )
