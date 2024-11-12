"""This file contains all enumeration types specified in OpenDRIVE."""
from enum import StrEnum


class RoadMarkColor(StrEnum):
    """Enumeration for the color of road markings."""

    INVALID = "invalid"
    BLACK = "black"
    BLUE = "blue"
    GREEN = "green"
    ORANGE = "orange"
    RED = "red"
    STANDARD = "standard"
    WHITE = "white"
    VIOLET = "violet"
    YELLOW = "yellow"


class RoadMarkType(StrEnum):
    """Enumeration for road marking types."""

    INVALID = "invalid"
    BOTTS_DOTS = "botts dots"
    BROKEN_BROKEN = "broken broken"
    BROKEN_SOLID = "broken solid"
    BROKEN = "broken"
    CURB = "curb"
    CUSTOM = "custom"
    edge = "edge"
    GRASS = "grass"
    NONE = "none"
    SOLID_BROKEN = "solid broken"
    SOLID_SOLID = "solid solid"
    SOLID = "solid"


class LaneChange(StrEnum):
    """Enumeration for lane change types."""

    INVALID = "invalid"
    BOTH = "both"
    DECREASE = "decrease"
    INCREASE = "increase"
    NONE = "none"


class Orientation(StrEnum):
    """Enumeration for orientation (relative to something else)."""

    PLUS = "+"
    MINUS = "-"
    NONE = "none"


class UnitDistance(StrEnum):
    """Enumeration for distance units."""

    FOOT = "ft"
    KILOMETER = "km"
    METER = "m"
    MILE = "mile"


class UnitSpeed(StrEnum):
    """Enumeration for speed units."""

    KM_PER_HOUR = "km/h"
    METER_PER_SECOND = "m/s"
    MILES_PER_HOUR = "mph"


class UnitMass(StrEnum):
    """Enumeration for mass units."""

    KILOGRAM = "kg"
    TON = "t"


class UnitSlope(StrEnum):
    """Enumeration for slope units."""

    PERCENT = "%"


CountryCode = str


class Unit(StrEnum):
    """An enumeration of all units (speed, distance, slope, mass)."""

    FOOT = "ft"
    KILOMETER = "km"
    METER = "m"
    MILE = "mile"
    KM_PER_HOUR = "km/h"
    METER_PER_SECOND = "m/s"
    MILES_PER_HOUR = "mph"
    KILOGRAM = "kg"
    TON = "t"
    PERCENT = "%"
