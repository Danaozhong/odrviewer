"""Stores functions to process OpenDRIVE roads."""
from typing import Dict, List, Optional, Set, Tuple

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from lxml import etree
from shapely.geometry import Polygon

from odrviewer.pyxodr.geometries import Arc, CubicPolynom, Line, MultiGeom, ParamCubicPolynom, Spiral
from odrviewer.pyxodr.geometries.base import Geometry
from odrviewer.pyxodr.road_objects.lane import ConnectionPosition, TrafficOrientation
from odrviewer.pyxodr.road_objects.lane_section import LaneSection
from odrviewer.pyxodr.signals.signal import Signal
from odrviewer.pyxodr.utils import cached_property
from odrviewer.pyxodr.utils.array import interpolate_path
from odrviewer.pyxodr.utils.curved_text import CurvedText


class Road:
    """Class representing a Road in an OpenDRIVE file.

    Parameters
    ----------
    road_xml : etree._Element
        XML element corresponding to this junction.
    resolution : float, optional
        Spatial resolution (in m) with which to create the road (and associated road
        object) coordinates, by default 0.1
    ignored_lane_types : Set[str], optional
        A set of lane types that should not be read from the OpenDRIVE file. If
        unspecified, no types are ignored.
    """

    def __init__(
        self,
        road_xml: etree._Element,
        resolution: float = 0.1,
        ignored_lane_types: Optional[Set[str]] = None,
    ):
        """Road constructor."""
        self.road_xml = road_xml
        self.resolution = resolution

        self.ignored_lane_types = set() if ignored_lane_types is None else ignored_lane_types

        # We'll store both successor and predecessor data as sometimes one of these
        # (maybe just successor?) will point to a junction rather than a road, so we
        # need the other to reconstruct the connectivity
        self.successor_data: Tuple[Road, Optional[ConnectionPosition]] = (None, None)
        self.predecessor_data: Tuple[Road, Optional[ConnectionPosition]] = (None, None)

    @cached_property
    def traffic_orientation(self) -> TrafficOrientation:
        """Get the traffic orientation (right/left-hand-drive) for this road.

        OpenDRIVE Spec Section 8: "The standard driving direction is defined by the
        value which is assigned to the @rule attribute (RHT=right-hand traffic,
        LHT=left-hand traffic)."

        Returns:
        -------
        TrafficOrientation
            Traffic orientation enum for this road.

        Raises:
        ------
        ValueError
            If an unknown OpenDRIVE traffic orientation string is found.
        """
        try:
            xodr_str_traffic_orientation = self["rule"]
        except KeyError:
            xodr_str_traffic_orientation = "RHT"
        if xodr_str_traffic_orientation == "RHT":
            traffic_orientation = TrafficOrientation.RIGHT
        elif xodr_str_traffic_orientation == "LHT":
            traffic_orientation = TrafficOrientation.LEFT
        else:
            raise ValueError(f"Unknown traffic orientation {xodr_str_traffic_orientation}: " + "expected RHT or LHT.")

        return traffic_orientation

    def __getitem__(self, name):
        """Easier access to the XML attributes."""
        return self.road_xml.attrib[name]

    def __hash__(self):
        """Calculates a hash based on the road ID."""
        return hash(self.id)

    def __repr__(self):
        """Returns a printable representation of the road ID."""
        return f"Road_{self.id}"

    @cached_property
    def reference_line(self) -> np.ndarray:
        """Generate the road reference line according to the OpenDRIVE standard (7.1).

        Returns:
        -------
        np.ndarray
            Reference line at resolution self.resolution

        Raises:
        ------
        NotImplementedError
            If a geometry is encountered which is not implemented.
        """
        geometry_coordinates = []
        for geometry in self.reference_line_geometries:
            geometry_coordinates.append(geometry.evaluate_geometry(self.resolution))

        geometry_coordinates = np.array(geometry_coordinates, dtype=object)

        stacked_coordinates = np.vstack(geometry_coordinates).astype(np.float64)
        stacked_coordinates = interpolate_path(stacked_coordinates, resolution=self.resolution)

        return stacked_coordinates

    @cached_property
    def reference_line_geometries(self) -> list[Geometry]:
        """Returns all geometry segments within the centerline."""
        geometry_element_distances = []
        geometries: list[Geometry] = []
        for geometry in self.road_xml.findall("planView/geometry"):
            # Note this is the length of the element's reference line
            length = float(geometry.attrib["length"])
            distance_along_reference_line = float(geometry.attrib["s"])
            x_global_offset = float(geometry.attrib["x"])
            y_global_offset = float(geometry.attrib["y"])
            heading_global_offset = float(geometry.attrib["hdg"])

            geometry_element_distances.append(distance_along_reference_line)
            if geometry.find("line") is not None:
                geometries.append(
                    Line(
                        x_offset=x_global_offset,
                        y_offset=y_global_offset,
                        heading_offset=heading_global_offset,
                        length=length,
                    )
                )
            elif geometry.find("arc") is not None:
                arc = geometry.find("arc")
                curvature = float(arc.attrib["curvature"])
                geometries.append(
                    Arc(
                        x_offset=x_global_offset,
                        y_offset=y_global_offset,
                        heading_offset=heading_global_offset,
                        length=length,
                        curvature=curvature,
                    )
                )
            elif geometry.find("poly3") is not None:
                poly3 = geometry.find("poly3")
                a = float(poly3.attrib["a"])
                b = float(poly3.attrib["b"])
                c = float(poly3.attrib["c"])
                d = float(poly3.attrib["d"])

                geometries.append(
                    CubicPolynom(
                        a=a,
                        b=b,
                        c=c,
                        d=d,
                        x_offset=x_global_offset,
                        y_offset=y_global_offset,
                        heading_offset=heading_global_offset,
                        length=length,
                    )
                )
            elif geometry.find("paramPoly3") is not None:
                poly3 = geometry.find("paramPoly3")
                a_u = float(poly3.attrib["aU"])
                b_u = float(poly3.attrib["bU"])
                c_u = float(poly3.attrib["cU"])
                d_u = float(poly3.attrib["dU"])

                a_v = float(poly3.attrib["aV"])
                b_v = float(poly3.attrib["bV"])
                c_v = float(poly3.attrib["cV"])
                d_v = float(poly3.attrib["dV"])

                p_range = poly3.attrib.get("pRange", "normalized")
                upper_p = 1.0 if p_range == "normalized" else length

                geometries.append(
                    ParamCubicPolynom(
                        a_u=a_u,
                        b_u=b_u,
                        c_u=c_u,
                        d_u=d_u,
                        a_v=a_v,
                        b_v=b_v,
                        c_v=c_v,
                        d_v=d_v,
                        x_offset=x_global_offset,
                        y_offset=y_global_offset,
                        heading_offset=heading_global_offset,
                        length=upper_p,
                    )
                )
            elif geometry.find("spiral") is not None:
                spiral = geometry.find("spiral")
                geometries.append(
                    Spiral(
                        curv_start=float(spiral.attrib["curvStart"]),
                        curv_end=float(spiral.attrib["curvEnd"]),
                        x_offset=x_global_offset,
                        y_offset=y_global_offset,
                        heading_offset=heading_global_offset,
                        length=length,
                    )
                )
            else:
                raise NotImplementedError

        geometry_element_distances = np.array(geometry_element_distances)

        geometry_element_distances.argsort()
        return geometries

    @cached_property
    def lane_offset_line(self) -> np.ndarray:
        """Generate the lane offset line according to the OpenDRIVE standard (9.3).

        Returns:
        -------
        np.ndarray
            Lane offset line at resolution self.resolution
        """
        lane_offsets = self.road_xml.findall("lanes/laneOffset")
        if lane_offsets == []:
            lane_offset_coordinates = self.reference_line
        else:
            offset_geometries = []
            offset_distances = []

            for lane_offset in lane_offsets:
                try:
                    s = float(lane_offset.attrib["s"])
                except KeyError:
                    s = float(lane_offset.attrib["sOffset"])
                offset_distances.append(s)

                a = float(lane_offset.attrib["a"])
                b = float(lane_offset.attrib["b"])
                c = float(lane_offset.attrib["c"])
                d = float(lane_offset.attrib["d"])

                offset_geometries.append(CubicPolynom(a, b, c, d))

            offset_multi_geometry = MultiGeom(offset_geometries, np.array(offset_distances))
            # Appears that direction==left is the standard, negative t when on RHS
            (
                lane_offset_coordinates,
                _,
            ) = offset_multi_geometry.global_coords_and_offsets_from_reference_line(
                self.reference_line,
                self.reference_line,
                self.reference_line,
                direction="left",
            )
        return lane_offset_coordinates

    @cached_property
    def z_coordinates(self) -> np.ndarray:
        """Generate the z coordinates of the reference line.

        According to the OpenDRIVE standard (Road Elevation: 8.4.1).

        Returns:
        -------
        np.ndarray
            Z coordinate, one per coordinate in self.reference_line
        """
        reference_line_direction_vectors = np.diff(self.reference_line, axis=0)
        reference_line_distances = np.cumsum(np.linalg.norm(reference_line_direction_vectors, axis=1))
        reference_line_distances = np.append(np.array([0.0]), reference_line_distances)

        elevation_profiles = self.road_xml.findall("elevationProfile/elevation")

        offset_distances = []

        offset_geometries = []

        for elevation_profile in elevation_profiles:
            try:
                s = float(elevation_profile.attrib["s"])
            except KeyError:
                s = float(elevation_profile.attrib["sOffset"])
            offset_distances.append(s)

            a = float(elevation_profile.attrib["a"])
            b = float(elevation_profile.attrib["b"])
            c = float(elevation_profile.attrib["c"])
            d = float(elevation_profile.attrib["d"])

            offset_geometries.append(CubicPolynom(a, b, c, d, 0.0, 0.0, 0.0))

        if offset_geometries != []:
            elevation_multi_geometry = MultiGeom(offset_geometries, np.array(offset_distances))

            _, z_values = elevation_multi_geometry(reference_line_distances).T
        else:
            z_values = np.zeros_like(self.reference_line[:, 0])

        return z_values

    @property
    def id(self):
        """Get the OpenDRIVE ID of this road."""
        return self["id"]

    def _link_lane_sections(self):
        """Connect all lane section objects within this road with their neighbours.

        Neighbours == the lane section objects corresponding to their successors and
        predecessors. This method will be called as part of the "connection" tree of
        calls. This method is called by _link_roads in RoadNetwork, which is the root
        of the tree.
        """
        # First lane section connects to the predecessor road
        # Also need to pay attention to the contact point - start means we connect to
        # the first lane section & vice versa
        if self.predecessor_data[0] is not None:
            predecessor_road, predecessor_connection_position = self.predecessor_data
            #
            connecting_lane_section = predecessor_road.lane_sections[predecessor_connection_position.index]
            # By definition of road linkage in OpenDRIVE (8.2), "A successor of a given
            # road is an element connected to the end of its reference line. A
            # predecessor of a given road is an element connected to the start of its
            # reference line. For junctions, different attribute sets shall be used for
            # the <predecessor> and <successor> elements."
            # Therefore as we are looking at <predecessor> data here, the connecting
            # lane section must be connected to the start of this road's reference line;
            # this corresponds to the start of the first lane section (which are
            # ordered along the reference line.)
            if predecessor_connection_position is ConnectionPosition.BEGINNING:
                connecting_lane_section.predecessor_data = (
                    self.lane_sections[0],
                    ConnectionPosition.BEGINNING,
                )
            else:
                connecting_lane_section.successor_data = (
                    self.lane_sections[0],
                    ConnectionPosition.BEGINNING,
                )
            self.lane_sections[0].predecessor_data = (
                connecting_lane_section,
                predecessor_connection_position,
            )
        # Then all pairs connect to each other
        for source_lane_section, target_lane_section in zip(self.lane_sections, self.lane_sections[1:]):
            source_lane_section.successor_data = (
                target_lane_section,
                ConnectionPosition.BEGINNING,
            )
            target_lane_section.predecessor_data = (
                source_lane_section,
                ConnectionPosition.END,
            )
        # Final lane section connects to the successor road
        if self.successor_data[0] is not None:
            successor_road, successor_connection_position = self.successor_data
            connecting_lane_section = successor_road.lane_sections[successor_connection_position.index]
            self.lane_sections[-1].successor_data = (
                connecting_lane_section,
                successor_connection_position,
            )
            if successor_connection_position is ConnectionPosition.BEGINNING:
                connecting_lane_section.predecessor_data = (
                    self.lane_sections[-1],
                    ConnectionPosition.END,
                )
            else:
                connecting_lane_section.successor_data = (
                    self.lane_sections[-1],
                    ConnectionPosition.END,
                )

        for lane_section in self.lane_sections:
            lane_section._link_lanes()

    def __partition_lane_offset_line_into_lane_sections(
        self,
    ) -> List[Tuple[etree._Element, np.ndarray, float, float]]:
        lane_section_distances = []
        for lane_section_xml in self.road_xml.findall("lanes/laneSection"):
            lane_section_distances.append(float(lane_section_xml.attrib["s"]))

        # Partition the reference line into subsections that fit into each
        # distance range
        reference_line_direction_vectors = np.diff(self.reference_line, axis=0)
        reference_line_distances = np.cumsum(np.linalg.norm(reference_line_direction_vectors, axis=1))
        # Make the same length as the original reference line
        reference_line_distances = np.insert(reference_line_distances, 0, 0)
        reference_line_length = np.sum(reference_line_distances[-1])
        lane_section_distances.append(reference_line_length)

        def get_sub_linestring(
            linestring: npt.NDArray[np.float32], lengths: npt.NDArray[np.float32], start: float, end: float
        ) -> npt.NDArray[np.float32]:
            # Find indices where the distances are greater than or equal to 'start' and less than or equal to 'end'
            start_idx = np.searchsorted(lengths, start, side="left")
            end_idx = np.searchsorted(lengths, end, side="right")
            if start_idx == 0 and end_idx == len(lengths) - 1:
                return linestring

            # Handle cases where start_idx or end_idx might be out of bounds or exact matches are needed
            rel_tol = 1e-8
            reuse_start_point = np.isclose(lengths[start_idx], start, atol=rel_tol) or start_idx == 0
            reuse_end_point = np.isclose(lengths[end_idx - 1], end, atol=rel_tol) or end_idx == len(lengths)

            def interpolate_point(exact_distance, distance_index):
                interp_t = (exact_distance - lengths[distance_index - 1]) / (
                    lengths[distance_index] - lengths[distance_index - 1]
                )
                return linestring[distance_index - 1] + interp_t * (
                    linestring[distance_index] - linestring[distance_index - 1]
                )

            # Interpolate start point if needed (if the exact start point isn't at an existing node)
            if not reuse_start_point:
                start_point = interpolate_point(start, start_idx)
                sub_linestring = [start_point] + list(linestring[start_idx:end_idx])
            else:
                sub_linestring = list(linestring[start_idx:end_idx])

            # Interpolate the end point if needed (same approach as start)
            if not reuse_end_point:
                end_point = interpolate_point(end, end_idx)
                sub_linestring.append(end_point)

            if len(sub_linestring) < 2:
                raise RuntimeError("sub linestring has less than two points")
            return np.array(sub_linestring)

        lane_section_tuples = []
        for i, lane_section_xml in enumerate(self.road_xml.findall("lanes/laneSection")):
            start_length = lane_section_distances[i]
            end_length = lane_section_distances[i + 1]

            if end_length > reference_line_length:
                end_length = reference_line_length

            if start_length >= end_length:
                # This segment doesn't make sense, there is no valid geometry associated with it
                # as a fallback, use some geometries at the end
                start_length = end_length - 0.1

            if start_length >= end_length:
                start_length = end_length - 0.1

            lane_section_tuples.append(
                (
                    lane_section_xml,
                    get_sub_linestring(self.lane_offset_line, reference_line_distances, start_length, end_length),
                    get_sub_linestring(self.z_coordinates, reference_line_distances, start_length, end_length),
                    get_sub_linestring(self.reference_line, reference_line_distances, start_length, end_length),
                    start_length,
                    end_length,
                )
            )
        return lane_section_tuples

    @cached_property
    def lane_sections(self) -> List[LaneSection]:
        """Return an ordered (along the reference line) list of lane sections.

        Returns:
        -------
        List[LaneSection]
            List of lane sections as they appear along the road reference line (in the
            s direction)
        """
        lane_sections = []
        for (
            i,
            (lane_section_xml, lane_sub_offset_line, lane_z_coordinates, lane_sub_reference_line, s_start, s_end),
        ) in enumerate(self.__partition_lane_offset_line_into_lane_sections()):
            lane_sections.append(
                LaneSection(
                    self.id,
                    i,
                    lane_section_xml,
                    lane_sub_offset_line,
                    lane_sub_reference_line,
                    lane_z_coordinates,
                    self.traffic_orientation,
                    ignored_lane_types=self.ignored_lane_types,
                    s_start=s_start,
                    s_end=s_end,
                )
            )

        return lane_sections

    @cached_property
    def successor_ids(self) -> Set[str]:
        """Get the OpenDRIVE IDs of the successor roads to this road."""
        _successor_ids = set()
        for successor_xml in self.road_xml.find("link").findall("successor"):
            _successor_ids.add(successor_xml.attrib["elementId"])
        return _successor_ids

    @cached_property
    def predecessor_ids(self) -> Set[str]:
        """Get the OpenDRIVE IDs of the predecessor roads to this road."""
        _predecessor_ids = set()
        for predecessor_xml in self.road_xml.find("link").findall("predecessor"):
            _predecessor_ids.add(predecessor_xml.attrib["elementId"])
        return _predecessor_ids

    @cached_property
    def boundary(self) -> Polygon:
        """Return the bounding polygon of this road."""
        left_borders = self.lane_borders["left"]
        if left_borders == []:
            left_borders = [self.reference_line]
        left_border = left_borders[-1]
        right_borders = self.lane_borders["right"]
        if right_borders == []:
            right_borders = [self.reference_line]
        right_border = np.flip(right_borders[-1], axis=0)
        bounding_poly = Polygon(np.vstack((left_border, right_border)))

        return bounding_poly

    @cached_property
    def junction_connecting_ids(self) -> Dict[str, Set[int]]:
        """Return the IDs of all junctions that connect to this road."""
        predecessor_junction_ids = [
            predecessor_xml.attrib["elementId"]
            for predecessor_xml in self.road_xml.find("link").findall("predecessor")
            if predecessor_xml.attrib["elementType"] == "junction"
        ]
        successor_junction_ids = [
            successor_xml.attrib["elementId"]
            for successor_xml in self.road_xml.find("link").findall("successor")
            if successor_xml.attrib["elementType"] == "junction"
        ]

        _junction_connecting_ids = {
            "predecessor": set(predecessor_junction_ids),
            "successor": set(successor_junction_ids),
        }

        return _junction_connecting_ids

    @property
    def signals(self) -> list[Signal]:
        """Returns the signals associated to the road."""
        if (signals_node := self.road_xml.find("signals")) is not None:
            return [Signal.from_xml_node(sig_node) for sig_node in signals_node.findall("signal")]
        return []

    def get_coordinate_and_direction(self, s: float) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]:
        """At a given s, returns the orientation of the reference line, and the direction vector."""
        reference_line_direction_vectors = np.diff(self.reference_line, axis=0)
        reference_line_distances = np.cumsum(np.linalg.norm(reference_line_direction_vectors, axis=1))
        reference_line_distances = np.insert(reference_line_distances, 0, 0)
        s_index = np.searchsorted(reference_line_distances, s)

        if s_index >= len(self.reference_line):
            s_index = len(self.reference_line) - 1

        # For the last point, use the previous direction vector
        dir_index = s_index
        if dir_index == len(self.reference_line) - 1:
            dir_index -= 1
        return self.reference_line[s_index], reference_line_direction_vectors[dir_index]

    def plot(
        self,
        axis: plt.Axes,
        plot_start_and_end: bool = False,
        line_scale_factor: float = 1.0,
        label_size: Optional[int] = None,
    ) -> plt.Axes:
        """Plot a visualisation of this road on a provided axis object.

        Parameters
        ----------
        axis : plt.Axes
            Axis on which to plot the road network.
        plot_start_and_end : bool, optional
            If True, plot both the start and end of roads (start with green dot, end
            with red cross), by default False
        line_scale_factor : float, optional
            Scale all lines thicknesses up by this factor, by default 1.0.
        label_size : int, optional
            If specified, text of this font size will be displayed along the road line
            of the form "r_n" where n is the ID of this road. By default None, resulting
            in no labels.

        Returns:
        -------
        plt.Axes
            Axis with the road plotted on it.
        """
        # Plot the road reference line.
        global_coords = self.reference_line
        global_coords_len = len(global_coords)
        axis.plot(*global_coords.T, linewidth=0.05 * line_scale_factor)
        if label_size is not None:
            x, y = global_coords[int(len(global_coords) // 2) - 1 :].T
            CurvedText(
                x=x,
                y=y,
                text=f"r_{self.id}",
                va="bottom",
                axes=axis,
                fontsize=3,
            )
        if plot_start_and_end:
            axis.scatter([global_coords[0][0]], [global_coords[0][1]], marker="o", c="green", s=4)
            axis.scatter([global_coords[-1][0]], [global_coords[-1][1]], marker="x", c="red", s=4)
        # Plot the road line directions
        origin_coordinate = global_coords[global_coords_len // 2]
        try:
            arrow_difference_vector = global_coords[global_coords_len // 2 + 1] - origin_coordinate
            axis.arrow(
                *origin_coordinate,
                *arrow_difference_vector,
                shape="full",
                lw=0.5,
                length_includes_head=True,
                head_width=0.5,
            )
        except IndexError as e:
            print(
                str(e)
                + " - this is likely caused by a road which is too short. "
                + "A direction arrow will not be printed for this road "
                + f"({self})."
                + "\nIf you're seeing lots of these errors, try a smaller "
                + "(finer) resolution."
            )

        # Plot the road offset line.
        axis.plot(
            *self.lane_offset_line.T,
            "-",
            label=f"{self}",
            linewidth=0.2 * line_scale_factor,
        )

        return axis
