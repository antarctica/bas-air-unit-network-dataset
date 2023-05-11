import re
import subprocess  # noqa: S404 (nonspecific warning)
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional

from importlib_resources import as_file as resource_path_as_file, files as resource_path
from lxml.etree import (  # noqa: S410, nosec - see 'lxml` package (bandit)' section in README
    Element,
    ElementTree,
    SubElement,
    tostring as element_string,
)


fpl_waypoint_types = ["USER WAYPOINT", "AIRPORT", "NDB", "VOR", "INT", "INT-VRP"]


def _upper_alphanumeric_space_only(value: str) -> str:
    """
    Strips non upper-case alphanumeric or space (' ') characters from string.

    E.g. 'FOO bar 12' would become 'FOO  12' (double space as we don't post-process values).

    :type value: str
    :param value: string to process
    :return: processed string
    """
    return re.sub(r"[^A-Z\d ]+", "", value.upper())


def _upper_alphanumeric_only(value: str) -> str:
    """
    Strips non upper-case alphanumeric characters from string.

    E.g. 'FOO bar 12' would become 'FOO12'.

    :type value: str
    :param value: string to process
    :return: processed string
    """
    return re.sub(r"[^A-Z\d]+", "", value.upper())


class Namespaces(object):
    """
    Namespaces for the Garmin FPL XML schema.

    This class defines XML namespaces and their corresponding schema (XSD) locations. It is a utility class to help
    generate encode FPL data in XML using the `lxml` library.
    """

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
        dict key (this is a lxml convention). This will create an invalid namespace map for use in XPath queries, this
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
        Generates the value for a `xsi:schemaLocation` attribute.

        Defines the XML Schema Document (XSD) for each namespace in an XML tree

        E.g. 'xsi:schemaLocation="http://www.w3.org/1999/xlink https://www.w3.org/1999/xlink.xsd"'

        :rtype: str
        :return: schema location attribute value
        """
        schema_locations = ""
        for prefix, location in Namespaces._schema_locations.items():
            schema_locations = f"{schema_locations} {Namespaces.namespaces[prefix]} {location}"

        return schema_locations.lstrip()


class Waypoint:
    """
    FPL waypoint.

    Concrete representation of an abstract waypoint using the FPL output format.
    """

    def __init__(
        self,
        identifier: Optional[str] = None,
        waypoint_type: Optional[str] = None,
        country_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> None:
        """
        Create FPL waypoint, optionally setting parameters.

        :type identifier: str
        :param identifier: unique identifier
        :type waypoint_type: str
        :param waypoint_type: waypoint type, typically 'USER WAYPOINT'
        :type country_code: str
        :param country_code: two digit country code waypoint resides, or '__' for Antarctica
        :type longitude: float
        :param longitude: longitude component of waypoint geometry
        :type latitude: float
        :param latitude: latitude component of waypoint geometry
        :type comment: str
        :param comment: Optional comment/description
        """
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
            self.waypoint_type = waypoint_type
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
        """
        FPL waypoint identifier.

        :rtype: str
        :returns waypoint identifier
        """
        return self._identifier

    @identifier.setter
    def identifier(self, identifier: str) -> None:
        """
        Sets FPL waypoint identifier.

        The FPL standard uses identifiers as foreign keys for referencing waypoints within routes, identifiers should
        therefore be unique values.

        The FPL standard restricts waypoint comments to 19 characters, however when listing waypoints, GPS devices may
        only display up to 17 characters. To avoid losing potentially crucial information, this library therefore
        considers 17 to be the effective limit, and will raise a ValueError exception if the length ia longer.

        Identifiers must consist of upper case alphanumeric characters (A-Z 0-9) only. Values containing invalid
        characters will be silently dropped.

        For example an identifier:
        > 'FOO-bar-ABCDEF' (14 characters)
        will become:
        > 'FOOABCDEF' (9 characters).

        :type identifier: str
        :param identifier: unique identifier
        """
        if identifier is not None:
            if len(identifier) > 12:
                raise ValueError("Identifier must be 12 characters or less.")
            self._identifier = _upper_alphanumeric_only(value=identifier)

    @property
    def waypoint_type(self) -> str:
        """
        FPL waypoint type.

        :rtype: str
        :returns waypoint type
        """
        return self._type

    @waypoint_type.setter
    def waypoint_type(self, waypoint_type: str) -> None:
        """
        Sets FPL waypoint type.

        The FPL standard defines several types of waypoint defined in the `fpl_waypoint_types` list and which include:
        - "USER WAYPOINT": user defined
        - "AIRPORT": airport
        - "INT": intersection
        - "VOR": Very High Frequency Omnidirectional Station
        - etc.

        Note: This library does not validate any requirements that might apply to specific waypoint types, other than
        what may be specified in the FPL XML XSD. Where types other than 'USER WAYPOINT' are used, is likely an
        apparently valid FPL can be generated by this library but which is marked invalid when imported into a device.

        :type waypoint_type: str
        :param waypoint_type: waypoint type, typically 'USER WAYPOINT'
        """
        if waypoint_type not in fpl_waypoint_types:
            raise ValueError(f"Waypoint type must be one of {' '.join(fpl_waypoint_types)!r}")

        self._type = waypoint_type

    @property
    def country_code(self) -> str:
        """
        FPL waypoint country code.

        This value may use a double underscore ('__') to represent countries such as Antarctica.

        :rtype: str
        :return: waypoint country code
        """
        return self._country_code

    @country_code.setter
    def country_code(self, country_code: str) -> None:
        """
        Used for organising and finding waypoints.

        The FPL standard restricts country codes to 2 characters, which must consist of upper case alphanumeric
        characters (A-Z 0-9) only. Values containing invalid characters will be silently dropped, except where noted
        below.

        A double underscore ('__') is sometimes used as the country code for Antarctica, rather than it's ISO 2-digit
        country code, 'AQ' (see #157 for more information). This value is invalid according to the FPL standard but has
        been used successfully in devices so is allowed as an exception to comply with existing usage.
        :type country_code: str
        :param country_code: two digit country code waypoint resides, or '__' for Antarctica
        """
        if country_code is not None:
            if len(country_code) > 2:
                raise ValueError("Country code must be 2 characters or less.")

        self._country_code = _upper_alphanumeric_only(value=country_code)

        # As an exception for Antarctica, we use '__' as the country code
        if country_code == "__":
            self._country_code = "__"

    @property
    def latitude(self) -> float:
        """
        Latitude component of FPL waypoint geometry.

        :rtype: float
        :returns waypoint geometry latitude
        """
        return self._latitude

    @latitude.setter
    def latitude(self, latitude: float) -> None:
        """
        Sets latitude component of waypoint geometry.

        The FPL standard assumes geometries are (single) points using the EPSG:4326 CRS. Values outside ±90 will raise
        a ValueError exception.

        **Note:** The FPL standard does not allow values to use `90.0` and `-90.0` exactly (for reasons best known to
        Garmin). This method will automatically convert values to be the closest values allowed (`±89.999999`).

        :type latitude: float
        :param latitude: latitude component of waypoint geometry
        """
        if latitude == 90:
            latitude = 89.999999
        elif latitude == -90:
            latitude = -89.999999

        self._latitude = latitude

    @property
    def longitude(self) -> float:
        """
        Longitude component of FPL waypoint geometry.

        :rtype: float
        :returns waypoint geometry longitude
        """
        return self._longitude

    @longitude.setter
    def longitude(self, longitude: float) -> None:
        """
        Sets longitude component of waypoint geometry.

        The FPL standard assumes geometries are (single) points using the EPSG:4326 CRS. Values outside ±180 will raise
        a ValueError exception.

        **Note:** The FPL standard does not allow values to use `180.0` and `-180.0` exactly (for reasons best known to
        Garmin). This method will automatically convert values to be the closest values allowed (`±179.999999`).

        :type longitude: float
        :param longitude: longitude component of waypoint geometry
        """
        if longitude == 90:
            longitude = 89.999999
        elif longitude == -90:
            longitude = -89.999999

        self._longitude = longitude

    @property
    def comment(self) -> str:
        """
        FPL waypoint comment.

        :rtype: str
        :returns waypoint comment
        """
        if self._comment is None:
            return "NO COMMENT"
        return self._comment

    @comment.setter
    def comment(self, comment: str) -> None:
        """
        Sets optional FPL waypoint comment.

        The FPL standard restricts waypoint comments to 25 characters, longer values will raise a ValueError exception.

        Comments must consist of upper case alphanumeric characters (A-Z 0-9), or spaces (' ') as a separator, only.
        Comments containing invalid characters will be silently dropped.

        For example a comment:
        > 'FOO-bar-ABC 123 DEF 456 G' (25 characters)
        will become:
        > 'FOOABC 123 DEF 456 G' (20 characters).

        :type comment: str
        :param comment: Optional comment/description
        """
        if len(comment) > 25:
            raise ValueError("Comments must be 25 characters or less.")

        self._comment = _upper_alphanumeric_space_only(value=comment)

    def encode(self) -> Element:
        """
        Build an XML element for the FPL waypoint.

        :rtype: Element
        :return: (L)XML element
        """
        waypoint = Element(f"{{{self.ns.fpl}}}waypoint", nsmap=self.ns.nsmap())

        identifier = SubElement(waypoint, f"{{{self.ns.fpl}}}identifier")
        identifier.text = self.identifier

        waypoint_type = SubElement(waypoint, f"{{{self.ns.fpl}}}type")
        waypoint_type.text = self.waypoint_type

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
    """
    FPL route waypoint.

    Concrete representation of an abstract route waypoint (waypoints within a route) using the FPL output format.
    """

    def __init__(
        self,
        waypoint_identifier: Optional[str] = None,
        waypoint_type: Optional[str] = None,
        waypoint_country_code: Optional[str] = None,
    ) -> None:
        """
        Create FPL route waypoint, optionally setting parameters.

        :type waypoint_identifier: str
        :param waypoint_identifier:
        :type waypoint_type: str
        :param waypoint_type:
        :type waypoint_country_code: str
        :param waypoint_country_code:
        """
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
        """
        Identifier of related FPL waypoint.

        :rtype: str
        :return: FPL waypoint identifier
        """
        return self._waypoint_identifier

    @waypoint_identifier.setter
    def waypoint_identifier(self, waypoint_identifier: str) -> None:
        if len(waypoint_identifier) > 12:
            raise ValueError("Waypoint identifier must be 12 characters or less.")
        """
        Sets reference to a FPL waypoint based on the waypoint identifier.

        As this value is a reference to an unknown set of waypoints, this value cannot be validated, except when loaded
        into the GPS device (which does have access to the set of waypoints).

        :type waypoint_identifier: str
        :param waypoint_identifier: FPL waypoint identifier
        """
        if len(waypoint_identifier) > 17:
            raise ValueError("Waypoint identifier must be 17 characters or less.")

        self._waypoint_identifier = _upper_alphanumeric_only(value=waypoint_identifier)

    @property
    def waypoint_type(self) -> str:
        """
        Type of related FPL waypoint.

        :rtype: str
        :return: FPL waypoint type
        """
        return self._waypoint_type

    @waypoint_type.setter
    def waypoint_type(self, waypoint_type: str) -> None:
        """
        Type for related FPL waypoint.

        See the main FPL Waypoint class for more information on setting this property.

        :type waypoint_type: str
        :param waypoint_type: FPL waypoint type
        """
        if waypoint_type not in fpl_waypoint_types:
            raise ValueError(f"Waypoint type must be one of {' '.join(fpl_waypoint_types)!r}")

        self._waypoint_type = waypoint_type

    @property
    def waypoint_country_code(self) -> str:
        """
        Country code for related FPL waypoint.

        See the main FPL Waypoint class for more information on return values.

        :rtype: str
        :return: FPL waypoint country code
        """
        return self._waypoint_country_code

    @waypoint_country_code.setter
    def waypoint_country_code(self, waypoint_country_code: str) -> None:
        """
        Country code for related FPL waypoint.

        See the main FPL Waypoint class for more information on setting this property.

            self._waypoint_country_code = _upper_alphanumeric_only(value=waypoint_country_code)
        :type waypoint_country_code: str
        :param waypoint_country_code:
        """
        if waypoint_country_code is not None:
            if len(waypoint_country_code) > 2:
                raise ValueError("Country code must be 2 characters or less.")

        self._waypoint_country_code = waypoint_country_code

        # As an exception for Antarctica, we use '__' as the country code
        if waypoint_country_code == "__":
            self._waypoint_country_code = "__"

    def encode(self) -> Element:
        """
        Build an XML element for the FPL route waypoint.

        :rtype: Element
        :return: (L)XML element
        """
        route_point = Element(f"{{{self.ns.fpl}}}route-point", nsmap=self.ns.nsmap())

        waypoint_identifier = SubElement(route_point, f"{{{self.ns.fpl}}}waypoint-identifier")
        waypoint_identifier.text = self.waypoint_identifier

        waypoint_type = SubElement(route_point, f"{{{self.ns.fpl}}}waypoint-type")
        waypoint_type.text = self.waypoint_type

        waypoint_country_code = SubElement(route_point, f"{{{self.ns.fpl}}}waypoint-country-code")
        waypoint_country_code.text = self.waypoint_country_code

        return route_point


class Route:
    """
    FPL route.

    Concrete representation of an abstract route using the FPL output format.

    See the abstract route class for general information on these properties and methods.
    """

    def __init__(
        self, name: Optional[str] = None, index: Optional[int] = None, points: Optional[List[dict]] = None
    ) -> None:
        """
        Create FPL route, optionally setting parameters.

        :type name: str
        :param name: name for route
        :type: index: int
        :param index: unique reference for route as an index value
        :type points: list
        :param points: optional list of route waypoints describing the path of the route (max: 3000)
        """
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
        """
        FPL route name.

        :rtype: str
        :returns route name
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Sets FPL route name.

        The FPL standard restricts route names to 25 characters, longer names will raise a ValueError exception.

        Names must consist of upper case alphanumeric characters (A-Z 0-9), or spaces (' ') as a separator, only. Names
        containing invalid characters will be silently dropped from names.

        For example a name:
        > 'FOO-bar-ABC 123 DEF 456 G' (25 characters)
        will become:
        > 'FOOABC 123 DEF 456 G' (20 characters).

        Note: The FPL standard uses spaces (' ') as a separator character, however the BAS Air Unit typically use
        underscores ('_') instead. This method will automatically (and silently) replace underscores with spaces to
        avoid this causing errors.

        # TODO: This logic should move to BAS specific classes, see #46.

        :type name: str
        :param name: route name, up to 25 uppercase alphanumeric or space separator characters only
        :raises ValueError: where the route name is over the 25 character limit
        """
        if len(name) > 25:
            raise ValueError("Name must be 25 characters or less.")

        # Handle BAS specific correction (see method description)
        name = name.replace("_", " ")

        self._name = _upper_alphanumeric_space_only(value=name)

    @property
    def index(self) -> int:
        """
        FPL route index.

        Uniquely identifies route across all other routes.

        :rtype: int
        :return: route index
        """
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        """
        Sets FPL route index.

        This index value uniquely identifies a route across all other routes. The FPL standard restricts route indexes
        to the range 0-98 (not 0-99), using whole integers. Values outside this range will raise a ValueError.

        :type index: int
        :param index: route index
        :raises ValueError: where the route index is outside the allowed range
        """
        if index > 99:
            raise ValueError("Index must be 98 or less.")

        self._index = index

    @property
    def points(self) -> List[RoutePoint]:
        """
        FPL route waypoints.

        The waypoints that make up the path of the route.

        :rtype list
        :return: set of waypoints that make up the route path
        """
        return self._points

    @points.setter
    def points(self, points: List[RoutePoint]) -> None:
        """
        Sets FPL route waypoints.

        See the RoutePoint class for more information.

        FPL routes may contain up to 3,000 waypoints. Where there are more than this a ValueError will be raised.

        Note: The logic implemented for this here is not failsafe, however it is validated more absolutely elsewhere.

        :type points: list
        :param points: FPL route waypoints
        :raises ValueError: where more than 3,000 waypoints are added
        """
        self._points = points

    def encode(self) -> Element:
        """
        Build an XML element for the FPL route.

        :rtype: Element
        :return: (L)XML element
        """
        route = Element(f"{{{self.ns.fpl}}}route", nsmap=self.ns.nsmap())

        route_name = SubElement(route, f"{{{self.ns.fpl}}}route-name")
        route_name.text = self.name

        route_index = SubElement(route, f"{{{self.ns.fpl}}}flight-plan-index")
        route_index.text = str(self.index)

        if len(self.points) > 3000:
            raise ValueError("FPL routes must have 3000 points or less.")

        for route_point in self.points:
            route.append(route_point.encode())

        return route


class Fpl:
    """
    Garmin Flight Plan (FPL).

    Used by Garmin aviation GPS units for loading waypoint and route information. FPLs are similar to, but more bespoke
    than, GPX files, with differences in structure and allowed properties / property values. For the purposes of this
    library, these differences amount to:

    - structuring information differently compared to GPX files
    - limiting the lengths of some values compared to GPX files
    - limiting the number of routes per file to one

    This implementation is quite simple and can be used to generate two types of FPL:

    1. an index of waypoints, with no route information, acts as lookup/reference for FPLs that define routes
    2. a route, which includes references to a FPL that defines waypoints

    For type (1) FPLs, this index includes an identifier, which acts as foreign key, and geometry information (to a
    fixed precision).

    For type (2) FPLs, routes reference waypoints via an identifier value and do not include geometry information
    directly.

    There is no formal link or reference between a type (1) and (2) file, instead all files are loaded together within
    the GPS device, meaning waypoints are shared across all routes and routes must be globally unique via an 'index'
    property (from 0 to 98, not 99).

    It is possible for a single FPL to contain both waypoints and routes, however this is not used operationally (at
    least not by the BAS Air Unit). There are other properties supported by FPLs which we don't yet support, such as
    authoring information and using different symbols. See #31 for more information.
    """

    def __init__(self, waypoints: Optional[List[Waypoint]] = None, route: Optional[Route] = None) -> None:
        """
        Create FPL, optionally setting parameters.

        :type waypoints: list
        :param waypoints: optional list of FPL waypoints
        :type route: list
        :param route: optional list of FPL routes
        """
        self.ns = Namespaces()

        with resource_path_as_file(resource_path("bas_air_unit_network_dataset.schemas.garmin")) as schema_dir:
            self.schema_path = schema_dir.joinpath("FlightPlanv1.xsd")

        self._waypoints: List[Waypoint] = []
        self._route: Optional[Route] = None

        if waypoints is not None:
            self.waypoints = waypoints

        if route is not None:
            self.route = route

    @property
    def waypoints(self) -> List[Waypoint]:
        """
        List of waypoints for FPLs that describe an index of waypoints (type 2).

        Note: these are a list of FPL specific representations of the waypoints.

        :rtype: list
        :return: Set of FPL waypoints
        """
        return self._waypoints

    @waypoints.setter
    def waypoints(self, waypoints: List[Waypoint]) -> None:
        """
        Sets waypoints for FPLs that describe an index of waypoints (type 1).

        :type waypoints: list
        :param waypoints: Set of FPL waypoints
        """
        self._waypoints = waypoints

    @property
    def route(self) -> Route:
        """
        The route set for FPLs that are describe routes (type 2).

        Note: this is an FPL specific representation of the route.

        :rtype: Route
        :return: FPL route
        """
        return self._route

    @route.setter
    def route(self, route: Route) -> None:
        """
        Sets the route for FPLs that are describe routes (type 2).

        :type route: Route
        :param route: FPL route
        """
        self._route = route

    def dumps_xml(self) -> bytes:
        """
        Build an XML element tree for the flight plan and generate an XML document.

        Elements for any waypoints and routes contained in the flight plan are added to a route element. An XML document
        is generated from this root, encoded as a UTF-8 byte string, with pretty-printing and an XML declaration.

        :rtype: bytes
        :return: XML document as byte string
        """
        root = Element(
            f"{{{self.ns.fpl}}}flight-plan",
            attrib={
                f"{{{self.ns.xsi}}}schemaLocation": self.ns.schema_locations(),
            },
            nsmap=self.ns.nsmap(),
        )

        if len(self.waypoints) > 1:
            waypoints_table = Element(f"{{{self.ns.fpl}}}waypoint-table")
            for waypoint in self.waypoints:
                waypoints_table.append(waypoint.encode())
            root.append(waypoints_table)

        if self.route is not None:
            root.append(self.route.encode())

        document = ElementTree(root)
        return element_string(document, pretty_print=True, xml_declaration=True, encoding="utf-8")

    def dump_xml(self, path: Path) -> None:
        """
        Write the flight plan to a file as XML.

        XML is the only supported file format for FPLs. This method is wrapper around the `dumps_xml()` method.

        :type path: Path
        :param path: XML output path
        """
        with open(path, mode="w") as xml_file:
            xml_file.write(self.dumps_xml().decode())

    def validate(self) -> None:
        """
        Validates the contents of a flight plan against a XSD schema.

        The external `xmllint` binary is used for validation as the `lxml` methods do not easily support relative paths
        for schemas that use imports/includes.

        Schemas are loaded from an XSD directory within this package using a backport of the `importlib.files` method.
        The current flight plan object is written as an XML file to a temporary directory to pass to xmllint.

        The xmllint binary returns a 0 exit code if the record validates successfully. Therefore, any other exit code
        can be, and is, considered a validation failure, raising a RuntimeError exception.

        :raises RuntimeError: where validation fails, message includes any stderr output from xmllint
        """
        with TemporaryDirectory() as document_path:
            document_path = Path(document_path).joinpath("fpl.xml")
            self.dump_xml(path=document_path)

            try:
                # Exempting Bandit/flake8 security issue (using subprocess)
                # It is assumed that there are other protections in place to prevent untrusted input being a concern.
                # Namely, that this package will be run in a secure/controlled environments against pre-trusted files.
                #
                # Use `capture_output=True` in future when we can use Python 3.7+
                subprocess.run(  # noqa: S274,S603 - nosec
                    args=["xmllint", "--noout", "--schema", str(self.schema_path), str(document_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Record validation failed: {e.stderr.decode()}") from e
