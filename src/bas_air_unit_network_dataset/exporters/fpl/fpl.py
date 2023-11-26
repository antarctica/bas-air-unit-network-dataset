from __future__ import annotations

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

from importlib_resources import path as resource_path
from lxml.etree import Element, ElementTree
from lxml.etree import tostring as element_string

from bas_air_unit_network_dataset.exporters.fpl import Namespaces
from bas_air_unit_network_dataset.exporters.fpl.route import Route
from bas_air_unit_network_dataset.exporters.fpl.waypoint import Waypoint


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

    def __init__(self, waypoints: Optional[list[Waypoint]] = None, route: Optional[Route] = None) -> None:
        """
        Create FPL, optionally setting parameters.

        :type waypoints: list
        :param waypoints: optional list of FPL waypoints
        :type route: list
        :param route: optional list of FPL routes
        """
        self.ns = Namespaces()

        with resource_path("bas_air_unit_network_dataset.exporters.fpl.schemas.garmin", "FlightPlanv1.xsd") as path:
            self.schema_path = path

        self._waypoints: list[Waypoint] = []
        self._route: Optional[Route] = None

        if waypoints is not None:
            self.waypoints = waypoints

        if route is not None:
            self.route = route

    @property
    def waypoints(self) -> list[Waypoint]:
        """
        List of waypoints for FPLs that describe an index of waypoints (type 2).

        Note: these are a list of FPL specific representations of the waypoints.

        :rtype: list
        :return: Set of FPL waypoints
        """
        return self._waypoints

    @waypoints.setter
    def waypoints(self, waypoints: list[Waypoint]) -> None:
        """
        Set waypoints for FPLs that describe an index of waypoints (type 1).

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
        Set the route for FPLs that are describe routes (type 2).

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
        with path.open(mode="w") as xml_file:
            xml_file.write(self.dumps_xml().decode())

    def validate(self) -> None:
        """
        Validate contents of a flight plan against a XSD schema.

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
                subprocess.run(
                    args=[
                        "xmllint",
                        "--noout",
                        "--schema",
                        str(self.schema_path),
                        str(document_path),
                    ],
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                msg = f"Record validation failed: {e.stderr.decode()}"
                raise RuntimeError(msg) from e
