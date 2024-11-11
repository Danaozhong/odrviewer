from enum import StrEnum
from itertools import chain


class RoadMarkColor(StrEnum):
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
    INVALID = "invalid"
    BOTH = "both"
    DECREASE = "decrease"
    INCREASE = "increase"
    NONE = "none"


class Orientation(StrEnum):
    PLUS = "+"
    MINUS = "-"
    NONE = "none"


class UnitDistance(StrEnum):
    FOOT = "ft"
    KILOMETER = "km"
    METER = "m"
    MILE = "mile"


class UnitSpeed(StrEnum):
    KM_PER_HOUR = "km/h"
    METER_PER_SECOND = "m/s"
    MILES_PER_HOUR = "mph"


class UnitMass(StrEnum):
    KILOGRAM = "kg"
    TON = "t"


class UnitSlope(StrEnum):
    PERCENT = "%"


CountryCode = str


class Unit(StrEnum):
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
