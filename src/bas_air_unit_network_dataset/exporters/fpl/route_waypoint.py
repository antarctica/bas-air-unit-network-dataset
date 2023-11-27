from __future__ import annotations

from typing import Optional

from lxml.etree import Element, SubElement

from bas_air_unit_network_dataset.exporters.fpl import Namespaces, fpl_waypoint_types
from bas_air_unit_network_dataset.exporters.fpl.utils import _upper_alphanumeric_only


class RouteWaypoint:
    """
    FPL route waypoint.

    Concrete representation of an abstract route waypoint (waypoints within a route) using the FPL output format.
    """

    max_identifier_length = 17
    max_country_code_length = 2
    max_comment_length = 25

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

        self._waypoint_reference: str
        self._waypoint_type: str
        self._waypoint_country_code: str

        if waypoint_identifier is not None:
            self.waypoint_reference = waypoint_identifier

        if waypoint_type is not None:
            self.waypoint_type = waypoint_type

        if waypoint_country_code is not None:
            self.waypoint_country_code = waypoint_country_code

    @property
    def waypoint_reference(self) -> str:
        """
        Identifier of related FPL waypoint.

        :rtype: str
        :return: FPL waypoint identifier
        """
        return self._waypoint_reference

    @waypoint_reference.setter
    def waypoint_reference(self, waypoint_identifier: str) -> None:
        """
        Set reference to a FPL waypoint based on the waypoint identifier.

        As this value is a reference to an unknown set of waypoints, this value cannot be validated, except when loaded
        into the GPS device (which does have access to the set of waypoints).

        :type waypoint_identifier: str
        :param waypoint_identifier: FPL waypoint identifier
        """
        if len(waypoint_identifier) > self.max_identifier_length:
            msg = f"Waypoint identifier must be {self.max_identifier_length} characters or less."
            raise ValueError(msg)

        self._waypoint_reference = _upper_alphanumeric_only(value=waypoint_identifier)

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
            msg = f"Waypoint type must be one of {' '.join(fpl_waypoint_types)!r}"
            raise ValueError(msg)

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

        :type waypoint_country_code: str
        :param waypoint_country_code: FPL waypoint country code
        """
        if len(waypoint_country_code) > self.max_country_code_length:
            msg = f"Country code must be {self.max_country_code_length} characters or less."
            raise ValueError(msg)

        self._waypoint_country_code = _upper_alphanumeric_only(value=waypoint_country_code)

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
        waypoint_identifier.text = self.waypoint_reference

        waypoint_type = SubElement(route_point, f"{{{self.ns.fpl}}}waypoint-type")
        waypoint_type.text = self.waypoint_type

        waypoint_country_code = SubElement(route_point, f"{{{self.ns.fpl}}}waypoint-country-code")
        waypoint_country_code.text = self.waypoint_country_code

        return route_point
