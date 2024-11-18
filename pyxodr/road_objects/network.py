"""This file stores all functions related to loading an OpenDRIVE map file."""
from typing import List, Optional, Set

from lxml import etree

from odrviewer.pyxodr.road_objects.junction import Junction
from odrviewer.pyxodr.road_objects.lane import ConnectionPosition
from odrviewer.pyxodr.road_objects.road import Road
from odrviewer.pyxodr.utils import cached_property


class RoadNetwork:
    """Class representing a road network from an entire OpenDRIVE file.

    Parameters
    ----------
    xodr_file_path : str
        Filepath to the OpenDRIVE file.
    resolution : float, optional
        Spatial resolution (in m) with which to create the road object coordinates, by
        default 0.1
    ignored_lane_types : Set[str], optional
        A set of lane types that should not be read from the OpenDRIVE file. If
        unspecified, no types are ignored.
    """

    def __init__(
        self,
        xodr_file_path: str,
        resolution: float = 0.1,
        ignored_lane_types: Optional[Set[str]] = None,
    ):
        """Constructor to to build an OpenDRIVE map from an '*.xodr' file."""
        self.tree = etree.parse(xodr_file_path)
        self.root = self.tree.getroot()

        self.resolution = resolution

        self.ignored_lane_types = set() if ignored_lane_types is None else ignored_lane_types

        self.road_ids_to_object = {}

    def get_inertial_value(self) -> tuple[float, float, float, float]:
        """Return the inertial values (north, south, east, west)."""
        odr_header = self.root.find("header").attrib
        return (
            float(odr_header["north"]),
            float(odr_header["south"]),
            float(odr_header["east"]),
            float(odr_header["west"]),
        )

    def get_geometry_reference(self) -> str:
        """Return the proj string in the header of the file."""
        return self.root.find("header").find("geoReference").text

    def get_offset(self) -> tuple[float, float, float, float]:
        """Return the offset as a tuple (x, y, z, heading)."""
        header_offset = self.root.find("header").find("offset").attrib
        return (
            float(header_offset["x"]),
            float(header_offset["y"]),
            float(header_offset["z"]),
            float(header_offset["hdg"]),
        )

    def get_junctions(self) -> List[Junction]:
        """Return the Junction objects for all junctions in this road network."""
        junctions = []
        for junction_xml in self.root.findall("junction"):
            junctions.append(
                Junction(
                    junction_xml,
                )
            )
        return junctions

    @cached_property
    def connecting_road_ids(self) -> Set[int]:
        """Return the IDs of all connecting roads in all junctions in this network."""
        _connecting_road_ids = set()
        for junction in self.get_junctions():
            _connecting_road_ids |= junction.get_connecting_road_ids()
        return _connecting_road_ids

    def _link_roads(self):
        """Link all roads to their neighbours.

        Neighbours == successor and predecessor roads.
        Also kicks off a tree of method calls that connects all other road elements
        to their neighbours. The next method in the call tree is _link_lane_sections.
        """
        for road in self.road_ids_to_object.values():
            link_xmls = road.road_xml.findall("link")
            if link_xmls == []:
                continue
            elif len(link_xmls) > 1:
                raise ValueError("Expected roads to link to only one other road")
            else:
                link_xml = link_xmls[0]
            pred_xmls = link_xml.findall("predecessor")
            if pred_xmls == []:
                pred_xml = None
            elif len(pred_xmls) > 1:
                raise ValueError("Expected roads to have only one predecessor road.")
            else:
                pred_xml = pred_xmls[0]
            succ_xmls = link_xml.findall("successor")
            if succ_xmls == []:
                succ_xml = None
            elif len(succ_xmls) > 1:
                raise ValueError("Expected roads to have only one successor road.")
            else:
                succ_xml = succ_xmls[0]

            pred_dict = pred_xml.attrib if pred_xml is not None else None
            succ_dict = succ_xml.attrib if succ_xml is not None else None

            if pred_dict is not None and pred_dict["elementType"] == "road":
                road.predecessor_data = (
                    self.road_ids_to_object[pred_dict["elementId"]],
                    ConnectionPosition.from_contact_point_str(pred_dict["contactPoint"]),
                )
            if succ_dict is not None and succ_dict["elementType"] == "road":
                road.successor_data = (
                    self.road_ids_to_object[succ_dict["elementId"]],
                    ConnectionPosition.from_contact_point_str(succ_dict["contactPoint"]),
                )

            road._link_lane_sections()

    def get_roads(
        self,
        include_connecting_roads: bool = True,
        verbose: bool = False,
    ) -> List[Road]:
        """Return the Road objects for all roads in this network."""
        ids_to_avoid = self.connecting_road_ids if not include_connecting_roads else set()
        roads = []
        iterator = self.root.findall("road")
        for road_xml in iterator:
            road_id = road_xml.attrib["id"]
            if road_id in ids_to_avoid:
                continue
            if road_id in self.road_ids_to_object:
                roads.append(self.road_ids_to_object[road_id])
            else:
                road = Road(
                    road_xml,
                    resolution=self.resolution,
                    ignored_lane_types=self.ignored_lane_types,
                )
                self.road_ids_to_object[road.id] = road
                roads.append(road)

        self._link_roads()

        return roads
