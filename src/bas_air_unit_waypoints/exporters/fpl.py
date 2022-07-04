from pathlib import Path
from typing import List, Optional

from lxml.etree import (
    Element,
    ElementTree,
    tostring as element_string,
    SubElement,
)  # nosec - see 'lxml` package (bandit)' section in README


class Namespaces(object):
    fpl = "http://www8.garmin.com/xmlschemas/FlightPlan/v1"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"

    _root_namespace = fpl

    _schema_locations = {
        "fpl": "http://www8.garmin.com/xmlschemas/FlightPlanv1.xsd",
    }

    namespaces = {
        "fpl": fpl,
        "xsi": xsi,
    }

    @staticmethod
    def nsmap(suppress_root_namespace: bool = False) -> dict:
        """
        Create a namespace map.

        Indexes namespaces by their prefix.

        E.g. {'xlink': 'http://www.w3.org/1999/xlink'}

        When a root namespace is set, a default namespace will be set by using the `None` constant for the relevant
        dict key (this is an lxml convention). This will create an invalid namespace map for use in XPath queries, this
        can be overcome using the `suppress_root_namespace` parameter, which will create a 'regular' map.

        :type suppress_root_namespace: bool
        :param suppress_root_namespace: When true, respects a root prefix as a default if set
        :return: dictionary of Namespaces indexed by prefix
        """
        nsmap = {}

        for prefix, namespace in Namespaces.namespaces.items():
            if namespace == Namespaces._root_namespace and not suppress_root_namespace:
                nsmap[None] = namespace
                continue

            nsmap[prefix] = namespace

        return nsmap

    @staticmethod
    def schema_locations() -> str:
        """
        Generates the value for a `xsi:schemaLocation` attribute

        Defines the XML Schema Document (XSD) for each namespace in an XML tree

        E.g. 'xsi:schemaLocation="http://www.w3.org/1999/xlink https://www.w3.org/1999/xlink.xsd"'

        :rtype str
        :return: schema location attribute value
        """
        schema_locations = ""
        for prefix, location in Namespaces._schema_locations.items():
            schema_locations = f"{schema_locations} {Namespaces.namespaces[prefix]} {location}"

        return schema_locations.lstrip()


class Waypoint:
    def __init__(
        self,
        identifier: Optional[str] = None,
        waypoint_type: Optional[str] = None,
        country_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        comment: Optional[str] = None,
    ):
        self.ns = Namespaces()

        self._identifier: Optional[str] = None
        self._type: Optional[str] = None
        self._country_code: Optional[str] = None
        self._latitude: Optional[float] = None
        self._longitude: Optional[float] = None
        self._comment: Optional[str] = None

        if identifier is not None:
            self.identifier = identifier
        if waypoint_type is not None:
            self.type = waypoint_type
        if country_code is not None:
            self.country_code = country_code
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        if comment is not None:
            self.comment = comment

    @property
    def identifier(self) -> str:
        return self._identifier

    @identifier.setter
    def identifier(self, identifier: str) -> None:
        self._identifier = identifier

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, waypoint_type: str) -> None:
        self._type = waypoint_type

    @property
    def country_code(self) -> str:
        return self._country_code

    @country_code.setter
    def country_code(self, country_code: str) -> None:
        self._country_code = country_code

    @property
    def latitude(self) -> float:
        return self._latitude

    @latitude.setter
    def latitude(self, latitude: float) -> None:
        self._latitude = latitude

    @property
    def longitude(self) -> float:
        return self._longitude

    @longitude.setter
    def longitude(self, longitude: float) -> None:
        self._longitude = longitude

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, comment: str) -> None:
        self._comment = comment

    def encode(self) -> Element:
        waypoint = Element(f"{{{self.ns.fpl}}}waypoint", nsmap=self.ns.nsmap())

        identifier = SubElement(waypoint, f"{{{self.ns.fpl}}}identifier")
        identifier.text = self.identifier

        waypoint_type = SubElement(waypoint, f"{{{self.ns.fpl}}}type")
        waypoint_type.text = self.type

        country_code = SubElement(waypoint, f"{{{self.ns.fpl}}}country-code")
        country_code.text = self.country_code

        latitude = SubElement(waypoint, f"{{{self.ns.fpl}}}lat")
        latitude.text = str(round(self.latitude, ndigits=7))

        longitude = SubElement(waypoint, f"{{{self.ns.fpl}}}lon")
        longitude.text = str(round(self.longitude, ndigits=7))

        if self.comment is not None:
            comment = SubElement(waypoint, f"{{{self.ns.fpl}}}comment")
            comment.text = self.comment

        return waypoint


class RoutePoint:
    def __init__(
        self,
        waypoint_identifier: Optional[str] = None,
        waypoint_type: Optional[str] = None,
        waypoint_country_code: Optional[str] = None,
    ):
        self.ns = Namespaces()

        self._waypoint_identifier: Optional[str] = None
        self._waypoint_type: Optional[str] = None
        self._waypoint_country_code: Optional[str] = None

        if waypoint_identifier is not None:
            self.waypoint_identifier = waypoint_identifier

        if waypoint_type is not None:
            self.waypoint_type = waypoint_type

        if waypoint_country_code is not None:
            self.waypoint_country_code = waypoint_country_code

    @property
    def waypoint_identifier(self) -> str:
        return self._waypoint_identifier

    @waypoint_identifier.setter
    def waypoint_identifier(self, waypoint_identifier: str) -> None:
        self._waypoint_identifier = waypoint_identifier

    @property
    def waypoint_type(self) -> str:
        return self._waypoint_type

    @waypoint_type.setter
    def waypoint_type(self, waypoint_type: str) -> None:
        self._waypoint_type = waypoint_type

    @property
    def waypoint_country_code(self) -> str:
        return self._waypoint_country_code

    @waypoint_country_code.setter
    def waypoint_country_code(self, waypoint_country_code: str) -> None:
        self._waypoint_country_code = waypoint_country_code

    def encode(self) -> Element:
        route_point = Element(f"{{{self.ns.fpl}}}route-point", nsmap=self.ns.nsmap())

        waypoint_identifier = SubElement(route_point, f"{{{self.ns.fpl}}}waypoint-identifier")
        waypoint_identifier.text = self.waypoint_identifier

        waypoint_type = SubElement(route_point, f"{{{self.ns.fpl}}}waypoint-type")
        waypoint_type.text = self.waypoint_type

        waypoint_country_code = SubElement(route_point, f"{{{self.ns.fpl}}}waypoint-country-code")
        waypoint_country_code.text = self.waypoint_country_code

        return route_point


class Route:
    def __init__(self, name: Optional[str] = None, index: Optional[int] = None, points: Optional[List[dict]] = None):
        self.ns = Namespaces()

        self._name: Optional[str] = None
        self._index: Optional[int] = None
        self._points: Optional[List[RoutePoint]] = []

        if name is not None:
            self.name = name

        if index is not None:
            self.index = index

        if points is not None:
            self.points = points

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        self._index = index

    @property
    def points(self) -> List[RoutePoint]:
        return self._points

    @points.setter
    def points(self, points: List[RoutePoint]):
        self._points = points

    def encode(self) -> Element:
        route = Element(f"{{{self.ns.fpl}}}route", nsmap=self.ns.nsmap())

        route_name = SubElement(route, f"{{{self.ns.fpl}}}route-name")
        route_name.text = self.name

        route_index = SubElement(route, f"{{{self.ns.fpl}}}flight-plan-index")
        route_index.text = str(self.index)

        for route_point in self.points:
            route.append(route_point.encode())

        return route


class Fpl:
    def __init__(self, waypoints: Optional[List[Waypoint]] = None, route: Optional[Route] = None):
        self.ns = Namespaces()

        self.root = Element(
            f"{{{self.ns.fpl}}}flight-plan",
            attrib={
                f"{{{self.ns.xsi}}}schemaLocation": self.ns.schema_locations(),
            },
            nsmap=self.ns.nsmap(),
        )

        self._waypoints: List[Waypoint] = []
        self._route: Optional[Route] = None

        if waypoints is not None:
            self.waypoints = waypoints

        if route is not None:
            self.route = route

    @property
    def waypoints(self) -> List[Waypoint]:
        return self._waypoints

    @waypoints.setter
    def waypoints(self, waypoints: List[Waypoint]):
        self._waypoints = waypoints

    @property
    def route(self) -> Route:
        return self._route

    @route.setter
    def route(self, route: Route) -> None:
        self._route = route

    def dumps_xml(self) -> bytes:
        """
        Generates an XML document and tree from the root XML element

        The XML document is encoded as a UTF-8 byte string, with pretty-printing and an XML declaration.

        :rtype bytes
        :return: XML document in bytes
        """
        if len(self.waypoints) > 1:
            waypoints_table = Element(f"{{{self.ns.fpl}}}waypoint-table")
            for waypoint in self.waypoints:
                waypoints_table.append(waypoint.encode())
            self.root.append(waypoints_table)

        if self.route is not None:
            self.root.append(self.route.encode())

        document = ElementTree(self.root)
        return element_string(document, pretty_print=True, xml_declaration=True, encoding="utf-8")

    def dump_xml(self, path: Path):
        with open(path, mode="w") as xml_file:
            xml_file.write(self.dumps_xml().decode())
