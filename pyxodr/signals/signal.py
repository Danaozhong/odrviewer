"""This file creates a model for traffic signal (i.e. signs and traffic lights)."""

from dataclasses import dataclass
from typing import Optional

from lxml.etree import _Element
from odrviewer.pyxodr.enumerations import CountryCode, Orientation, Unit


@dataclass
class Signal:
    """Represents a Signal according to OpenDRIVE 1.8.1 Specification."""

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

    def from_xml_node(self: _Element) -> "Signal":
        """Loads a signal from an lxml node."""
        return Signal(
            country_revision=self.get("countryRevision", None),
            country=self.get("country", None),
            dynamic=self.get("dynamic", False),
            h_offset=self.get("hOffset", None),
            height=self.get("height", None),
            id=self.get("id", "invalid_id"),
            length=self.get("length", None),
            name=self.get("name", None),
            orientation=self.get("orientation", None),
            pitch=self.get("pitch", None),
            roll=self.get("roll", None),
            s=float(self.get("s", 0.0)),
            subtype=self.get("subtype", ""),
            t=float(self.get("t", 0.0)),
            text=self.get("text", None),
            type=self.get("type", "none"),
            unit=self.get("unit", None),
            value=self.get("value", None),
            width=self.get("width", None),
            z_offset=float(self.get("zOffset", 0.0)),
        )
