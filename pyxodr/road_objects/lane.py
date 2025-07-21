"""This file stored functionality related to parsing/visualizing an OpenDRIVE lane."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import numpy as np
from lxml import etree
from odrviewer.pyxodr.enumerations import LaneChange, RoadMarkColor, RoadMarkType
from odrviewer.pyxodr.geometries import CubicPolynom, MultiGeom
from odrviewer.pyxodr.utils import cached_property


class LaneOrientation(Enum):
    """Enum representing whether a lane is left or right of the reference line."""

    LEFT = 0
    RIGHT = 1


class TrafficOrientation(Enum):
    """Enum representing whether a road is right-hand-drive or left-hand-drive.

    If right hand drive, lanes with positive IDs will have their centre line directions
    flipped (as these lanes will be on the left of the road reference line
    and should be going in the opposite direciton to it).
    """

    RIGHT = 0
    LEFT = 1


class ConnectionPosition(Enum):
    """Whether a connection connects to the beginning or end of a specified object."""

    BEGINNING = 0
    END = -1

    @classmethod
    def from_contact_point_str(cls, contact_point_str: str) -> ConnectionPosition:
        """Create a ConnectionPosition enum from an OpenDRIVE e_contactPoint string.

        See OpenDRIVE Spec Table 105.

        Parameters
        ----------
        contact_point_str : str
            e_contactPoint string.

        Returns:
        -------
        ConnectionPosition
            Connection Position enum.

        Raises:
        ------
        ValueError
            If an unknown contact point string is passed in.
        """
        if contact_point_str == "end":
            return cls.END
        elif contact_point_str == "start":
            return cls.BEGINNING
        else:
            raise ValueError(f"Unknown contact point str {contact_point_str}: " + "expected 'end' or 'start'.")

    @property
    def index(self):
        """Get the numerical index, to be used to index a list."""
        return self.value


@dataclass
class RoadMark:
    """Stores a road marking OpenDRIVE attribute (e.g. a lane line or curb)."""

    color: RoadMarkColor
    height: float | None
    lane_change: LaneChange | None
    material: str | None
    s_offset: float
    type: RoadMarkType
    weight: float | None
    width: float | None


class Lane:
    """Class representing a Lane in an OpenDRIVE file.

    Parameters
    ----------
    road_id : int
        Parent road ID.
    lane_section_id : int
        Parent lane section ID (ordinal - see lane_section_ordinal description in
        the LaneSection class docstring).
    lane_xml : etree._Element
        XML element corresponding to this lane.
    lane_offset_line : np.ndarray
        Offset line of this lane. This will be a sub-section of the lane offset line
        (OpenDRIVE spec 9.3) that just covers the parent lane section, rather than
        the whole road.
    lane_section_reference_line : np.ndarray
        Reference line of this lane. This will be a sub-section of the road
        reference line (OpenDRIVE spec 7.1) that just covers the parent lane
        section, rather than the whole road.
    orientation : LaneOrientation
        Enum representing if this lane is on the left or the right of the reference
        line.
    traffic_orientation: TrafficOrientation
        The traffic orientation (right/left-hand-drive) for this lane. See
        OpenDRIVE Spec Section 8.
    lane_z_coords : np.ndarray
        z coordinates of the reference line of this lane. This will be the z coordinates
        of a sub-section of the road reference line (OpenDRIVE spec 7.1) that just
        covers the parent lane section, rather than the whole road.
    inner_lane : Lane, optional
        The Lane on the inside edge of this lane (one further to the road reference
        line), by default None
    """

    def __init__(
        self,
        road_id: int,
        lane_section_id: int,
        lane_xml: etree._Element,
        lane_offset_line: np.ndarray,
        lane_section_reference_line: np.ndarray,
        orientation: LaneOrientation,
        traffic_orientation: TrafficOrientation,
        lane_z_coords: np.ndarray,
        inner_lane: Lane = None,
        s_start: float = 0.0,
        s_end: float | None = None,
    ):
        """Constructor."""
        self.road_id = road_id
        self.lane_section_id = lane_section_id
        self.lane_xml = lane_xml
        self.orientation = orientation
        self.traffic_orientation = traffic_orientation
        self.lane_offset_line = lane_offset_line
        self.lane_section_reference_line = lane_section_reference_line
        self.lane_z_coords = lane_z_coords
        self.s_start = s_start
        self.s_end = s_end

        if inner_lane is None:
            self.lane_reference_line = lane_offset_line
        else:
            self.lane_reference_line = inner_lane.boundary_line

        self.successor_data: list[tuple[Lane, str]] = []
        self.predecessor_data: list[tuple[Lane, str]] = []

    def __getitem__(self, name):
        """Returns a lane attribute, if set."""
        return self.lane_xml.attrib[name]

    def __hash__(self):
        """Creates a unique hash based on a tuple of road, lane section and lane IDs."""
        return hash((self.road_id, self.lane_section_id, self.id))

    def __repr__(self):
        """Human-readable representation of the Lane."""
        return f"Lane_{self.id}/Section_{self.lane_section_id}/Road_{self.road_id}"

    @property
    def id(self):
        """Get the OpenDRIVE ID of this lane."""
        return int(self["id"])

    @property
    def successor_ids(self) -> list[int]:
        """Get the OpenDRIVE IDs of the successor lanes to this lane."""
        return self._get_connecting_ids("successor")

    @property
    def predecessor_ids(self) -> list[int]:
        """Get the OpenDRIVE IDs of the predecessor lanes to this lane."""
        return self._get_connecting_ids("predecessor")

    def _get_connecting_ids(self, connecting_key: Literal["successor", "predecessor"]):
        link_xml = self.lane_xml.find("link")
        if link_xml is None:
            return []
        # Note connections to and from lane ID 0 should not be allowed, therefore we
        # will ignore them; the OpenDRIVE spec states
        # "Lane predecessors and successors shall only be used to connect lanes if a
        # physical connection at the beginning or end of both lanes exist. Both lanes
        # have a non-zero width at the connection point and they are semantically
        # connected."
        # And also states that "The center lane has no width and serves as reference
        # for lane numbering. The center lane itself has the lane id 0."
        # If I'm wrong about this, please raise an issue.
        if self.id == 0:
            return []
        connecting_ids = []
        for connecting_xml in link_xml.findall(connecting_key):
            int_id = int(connecting_xml.attrib["id"])
            if int_id != 0:
                connecting_ids.append(int_id)
        return connecting_ids

    @cached_property
    def type(self) -> str:
        """Get the OpenDRIVE type of this lane."""
        lane_type = self.lane_xml.attrib["type"]
        if lane_type == "none":
            lane_type = None
        return lane_type

    @cached_property
    def boundary_line(self) -> Optional[np.ndarray]:
        """Return the boundary line of this lane.

        Note this is the _far_ boundary, i.e. furthest from the road centre

        Returns:
        -------
        np.ndarray
            Boundary of the far edge of the lane.
        """
        return self.get_boundary_line_segment()

    def get_boundary_line_segment(self, s_start=0.0, s_end=None) -> Optional[np.ndarray]:
        """Returns a subset of boundary geometry, based on a range for the 's' parameter."""
        if self.lane_section_reference_line is None:
            # No valid geometry, but we will tolerate it for now.
            return None

        if len(self.lane_section_reference_line) < 2:
            # If there is a geometry, it must be valid.
            raise IndexError(f"Zero length reference line in lane {self}")

        lane_uses_widths = self.lane_xml.findall("width") != []
        lane_uses_borders = self.lane_xml.findall("border") != []

        if lane_uses_widths and lane_uses_borders:
            raise NotImplementedError(f"{self} seems to use both widths and borders; unsupported.")
        elif not lane_uses_widths and not lane_uses_borders:
            if self.type is None:
                return self.lane_section_reference_line
            raise NotImplementedError(
                f"{self} seems to use neither widths nor borders; unsupported " + "(for type!=none)."
            )

        lane_geometries: list[CubicPolynom] = []
        lane_distances: list[float] = []

        for element in self.lane_xml.findall("width" if lane_uses_widths else "border"):
            try:
                s = float(element.attrib["s"])
            except KeyError:
                s = float(element.attrib["sOffset"])
            a = float(element.attrib["a"])
            b = float(element.attrib["b"])
            c = float(element.attrib["c"])
            d = float(element.attrib["d"])

            lane_geometries.append(CubicPolynom(a, b, c, d))
            lane_distances.append(s)

        lane_multi_geometry = MultiGeom(lane_geometries, np.array(lane_distances))
        (
            global_lane_coords,
            _,
        ) = lane_multi_geometry.global_coords_and_offsets_from_reference_line(
            self.lane_section_reference_line,
            self.lane_offset_line,
            self.lane_reference_line if lane_uses_widths else self.lane_offset_line,
            direction="left" if self.orientation is LaneOrientation.LEFT else "right",
            s_start=s_start,
            s_end=s_end,
        )

        return global_lane_coords

    @cached_property
    def centre_line(self) -> np.ndarray:
        """Return the centre line of this lane.

        Centre line is computed as halfway between the lane reference line and the lane
        boundary.

        Returns:
        -------
        np.ndarray
            Coordinates of the lane centre line.
        """
        lane_centre_xy = np.mean((self.lane_reference_line, self.boundary_line), axis=0)
        lane_centre = np.append(lane_centre_xy, self.lane_z_coords[:, np.newaxis], axis=1)
        return lane_centre

    @property
    def _traffic_flows_in_opposite_direction_to_centre_line(self) -> bool:
        """Return bool representing whether traffic flows in opposite direction to centre.

        Considering the traffic orientation (RHT or LHT) and whether this lane is to the
        right or to the left of the centre line.

        Returns:
        -------
        bool
            True if the traffic flows in the opposite direction to the centre line.
        """
        # Negative ID means to the right of the road reference line.
        traffic_flows_in_opposite_direction_to_centre_line = (self.id < 0) != (
            self.traffic_orientation is TrafficOrientation.RIGHT
        )
        return traffic_flows_in_opposite_direction_to_centre_line

    @property
    def traffic_flow_line(self) -> np.ndarray:
        """Return the centre line in the direction along which traffic would flow.

        Returns:
        -------
        np.ndarray
            Coordinates of the centre line in the order of (legal) traffic flow.
        """
        if self._traffic_flows_in_opposite_direction_to_centre_line:
            traffic_flow_line = np.flip(self.centre_line, axis=0)
        else:
            traffic_flow_line = self.centre_line

        return traffic_flow_line

    @property
    def traffic_flow_successors(self) -> set[Lane]:
        """Return the successors of this lane that traffic could legally flow to.

        Returns:
        -------
        Set[Lane]
            Set of successor lanes according to traffic flow.
        """
        successor_lanes = set()
        if self._traffic_flows_in_opposite_direction_to_centre_line:
            successor_data = self.predecessor_data
        else:
            successor_data = self.successor_data

        for lane, connection_position in successor_data:
            if lane._traffic_flows_in_opposite_direction_to_centre_line:
                if connection_position is not ConnectionPosition.END:
                    raise ValueError(
                        f"Expected {self} to connect to the end of {lane}, "
                        + "after flipping it according to traffic flow direction."
                    )
            else:
                if connection_position is not ConnectionPosition.BEGINNING:
                    raise ValueError(f"Expected {self} to connect to the start of {lane}.")

            successor_lanes.add(lane)

        return successor_lanes

    @property
    def road_marks(self) -> list[RoadMark]:
        """Returns the road marks associated to the lane. List is sorted by the `sOffset`."""
        road_marks: list[RoadMark] = []
        for road_mark_xml in self.lane_xml.findall("roadMark"):
            road_marks.append(
                RoadMark(
                    color=road_mark_xml.get("color", RoadMarkColor.INVALID),
                    height=float(road_mark_xml.get("height", 0.0)),
                    lane_change=road_mark_xml.get("laneChange", None),
                    material=road_mark_xml.get("material", None),
                    s_offset=float(road_mark_xml.get("sOffset", 0.0)),
                    type=road_mark_xml.get("type", RoadMarkType.INVALID),
                    weight=road_mark_xml.get("weight", None),
                    width=road_mark_xml.get("width", None),
                )
            )
        return sorted(road_marks, key=lambda x: x.s_offset)
