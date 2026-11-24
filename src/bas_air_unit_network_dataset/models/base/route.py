from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

from geojson import Feature
from geojson.geometry import LineString

from bas_air_unit_network_dataset.models.base.route_waypoint import RouteWaypoint
from bas_air_unit_network_dataset.models.base.waypoint import Waypoint


@dataclass
class Route:
    """
    A known, planned, path between an origin and destination location.

    Routes are containers or namespaces identifying a path that has been pre-planned. Each route has a name and a list
    of RouteWaypoint instances representing the locations that make up its path.

    Routes are templates of paths that can then be followed in a particular journey, each forming a track (and are a
    distinct concept not represented by this library). Routes typically represent regularly travelled paths but this
    isn't required.

    Routes are not spatial features directly, but a linestring geometry can be derived from the point geometry of each
    waypoint associated with the route.

    This class is an abstract representation of a route concept, independent of any specific formats or encodings. It
    includes methods for representing the route and its path - either whole or as origin and destination waypoints.

    Properties:
    - `name`: descriptive name for the route
    - `waypoints`: route waypoints, listed in route order

    See the 'Information Model' section of the library README for more information.
    """

    name: str
    waypoints: list[RouteWaypoint] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Post-initialisation validation and processing."""
        if len(self.waypoints) < 1:
            msg = "Routes must contain at least one waypoint."
            raise ValueError(msg) from None

    def __repr__(self) -> str:
        """String representation."""
        start = self.first_waypoint.waypoint.identifier.ljust(6)
        end = self.last_waypoint.waypoint.identifier.ljust(6)

        return f"<Route {self.name.ljust(10, '_')} :- {len(self.waypoints)} waypoints, Start/End: {start} / {end}>"

    def __len__(self) -> int:
        """Waypoints in route."""
        return len(self.waypoints)

    @property
    def first_waypoint(self) -> RouteWaypoint:
        """First waypoint in route."""
        return self.waypoints[0]

    @property
    def last_waypoint(self) -> RouteWaypoint:
        """
        Last waypoint in route.

        Routes may consist of a single waypoint, in which case this property will return the same waypoint as
        `first_waypoint` property.
        """
        return self.waypoints[-1]

    @staticmethod
    def _resolve_waypoints(geom: LineString, waypoints: list[Waypoint]) -> list[RouteWaypoint]:
        """
        Determine waypoints within a route based on waypoint coordinates.

        Finds a waypoint corresponding to each node within a linestring geometry, preserving node order.

        Coordinates must therefore:
        - match exactly, including precision
        - not overlap
        """
        _index: dict[tuple[float, float], Waypoint] = {(wp.geometry.x, wp.geometry.y): wp for wp in waypoints}
        route = []
        for node in geom.coordinates:
            wp = _index[(node[0], node[1])]
            route.append(RouteWaypoint(waypoint=wp))

        return route

    @classmethod
    def loads_feature(cls, feature: Feature, reference_waypoints: list[Waypoint]) -> Self:
        """Create a Route from a GeoJSON linestring feature and reference Waypoints."""
        return Route(
            name=feature.properties["identifier"],
            waypoints=Route._resolve_waypoints(geom=feature.geometry, waypoints=reference_waypoints),
        )
