from __future__ import annotations

import subprocess
from importlib.resources import path as resource_path
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from lxml.etree import Element, ElementTree
from lxml.etree import tostring as element_string

from bas_air_unit_network_dataset.exporters.fpl import Namespaces

if TYPE_CHECKING:
    from bas_air_unit_network_dataset.models.formats.fpl import Route, Waypoint


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
    property.

    It is possible for a single FPL to contain both waypoints and routes, however this is not used operationally (at
    least not by the BAS Air Unit). There are other properties supported by FPLs which we don't yet support, such as
    authoring information and using different symbols. See #31 for more information.
    """

    ns = Namespaces()

    def __init__(self, waypoints: list[Waypoint] | None = None, route: Route | None = None) -> None:
        """Create FPL, with either a set of waypoints (type 1 files) or a route (type 2)."""
        with resource_path("bas_air_unit_network_dataset.exporters.fpl", "__init__.py") as path:
            self.schema_path = path.parent.joinpath("schemas/garmin/FlightPlanv1.xsd")

        self._waypoints: list[Waypoint] = waypoints or []
        self._route: Route | None = route

    def dumps(self) -> bytes:
        """
        Build an XML element for a FPL flight plan.

        Elements for any waypoints and routes are included as needed.

        Returned as an XML document, encoded as a UTF-8 byte string, with pretty-printing and an XML declaration.
        """
        root = Element(
            f"{{{self.ns.fpl}}}flight-plan",
            attrib={
                f"{{{self.ns.xsi}}}schemaLocation": self.ns.schema_locations(),
            },
            nsmap=self.ns.nsmap(),
        )

        if len(self._waypoints) > 0:
            waypoints_table = Element(f"{{{self.ns.fpl}}}waypoint-table")
            for waypoint in self._waypoints:
                waypoints_table.append(waypoint.dumps())
            root.append(waypoints_table)

        if self._route is not None:
            root.append(self._route.dumps())

        document = ElementTree(root)
        return element_string(document, pretty_print=True, xml_declaration=True, encoding="utf-8")

    def validate(self) -> None:
        """
        Validate a flight plan against the FPL XSD schema.

        The external `xmllint` binary is used for validation as `lxml` methods do not easily support relative paths for
        schemas that use imports/includes.

        Schemas are loaded from an XSD directory within this package. The current flight plan is written to a temporary
        directory to pass to xmllint.

        xmllint returns a 0 exit code if the record validates successfully - any other exit code is considered a
        validation failure, raising a RuntimeError exception.
        """
        with TemporaryDirectory() as tmp_path:
            document_path = Path(tmp_path).joinpath("fpl.xml")
            with document_path.open(mode="w") as f:
                f.write(self.dumps().decode())

            try:
                # Exempting Bandit/flake8 security issue (using subprocess)
                # It is assumed that there are other protections in place to prevent untrusted input being a concern.
                # Namely, that this package will be run in a secure/controlled environments against pre-trusted files.
                subprocess.run(  # noqa: S603
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
