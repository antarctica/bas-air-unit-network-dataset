from __future__ import annotations

from dataclasses import dataclass

from bas_air_unit_network_dataset.models.base.waypoint import Waypoint


@dataclass
class RouteWaypoint:
    """
    A Waypoint within a Route.

    Route waypoints link a particular Waypoint to a particular Route, including contextual information on where with
    the route a waypoint appears (i.e. at the beginning, end or somewhere inbetween).

    Waypoint order is held by the Route's list, following the input linestring node order.

    This class handles singular waypoints/positions within a route. All waypoints and positions within a route are
    managed by the Route class.

    See the 'Information Model' section of the library README for more information.
    """

    waypoint: Waypoint
