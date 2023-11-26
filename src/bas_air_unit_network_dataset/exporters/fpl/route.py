from __future__ import annotations

from typing import Optional

from lxml.etree import Element, SubElement

from bas_air_unit_network_dataset.exporters.fpl import Namespaces
from bas_air_unit_network_dataset.exporters.fpl.route_waypoint import RouteWaypoint
from bas_air_unit_network_dataset.exporters.fpl.utils import (
    _upper_alphanumeric_space_only,
)


class Route:
    """
    FPL route.

    Concrete representation of an abstract route using the FPL output format.

    See the abstract route class for general information on these properties and methods.
    """

    max_route_waypoints = 3_000

    def __init__(
        self,
        name: Optional[str] = None,
        index: Optional[int] = None,
        points: Optional[list[dict]] = None,
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
        self._points: Optional[list[RouteWaypoint]] = []

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
        Set FPL route name.

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
            msg = "Name must be 25 characters or less."
            raise ValueError(msg)

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
        Set FPL route index.

        This index value uniquely identifies a route across all other routes. The FPL standard restricts route indexes
        to the range 0-98 (not 0-99), using whole integers. Values outside this range will raise a ValueError.

        :type index: int
        :param index: route index
        :raises ValueError: where the route index is outside the allowed range
        """
        if index > 99:
            msg = "Index must be 98 or less."
            raise ValueError(msg)

        self._index = index

    @property
    def points(self) -> list[RouteWaypoint]:
        """
        FPL route waypoints.

        The waypoints that make up the path of the route.

        :rtype list
        :return: set of waypoints that make up the route path
        """
        return self._points

    @points.setter
    def points(self, points: list[RouteWaypoint]) -> None:
        """
        Set FPL route waypoints.

        See the RoutePoint class for more information.

        FPL routes may contain up to 3,000 waypoints. Where there are more than this a ValueError will be raised.

        Note: The logic implemented for this here is not failsafe, however it is validated more absolutely elsewhere.

        :type points: list
        :param points: FPL route waypoints
        :raises ValueError: where more than 3,000 waypoints are added
        """
        if len(points) > self.max_route_waypoints:
            msg = f"FPL routes must have {self.max_route_waypoints} waypoints or fewer."
            raise ValueError(msg)

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

        if len(self.points) > self.max_route_waypoints:
            msg = f"FPL routes must have {self.max_route_waypoints} waypoints or fewer."
            raise ValueError(msg)

        for route_point in self.points:
            route.append(route_point.encode())

        return route
