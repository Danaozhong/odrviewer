from enum import StrEnum

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