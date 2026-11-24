from dataclasses import dataclass
from typing import Self

from gpxpy.gpx import GPXRoute, GPXRoutePoint, GPXWaypoint

from bas_air_unit_network_dataset.models.base.route import Route as BaseRoute
from bas_air_unit_network_dataset.models.base.route_waypoint import RouteWaypoint as BaseRouteWaypoint
from bas_air_unit_network_dataset.models.base.waypoint import Waypoint as BaseWaypoint


@dataclass
class Waypoint:
    """Waypoint for use in a GPX document."""

    identifier: str
    longitude: float
    latitude: float
    name: str | None
    comment: str | None = None

    @classmethod
    def loads(cls, waypoint: BaseWaypoint) -> Self:
        """Load a base waypoint as a GPX waypoint."""
        return Waypoint(
            identifier=waypoint.identifier,
            name=waypoint.name,
            longitude=waypoint.geometry.x,
            latitude=waypoint.geometry.y,
            comment=waypoint.comment,
        )

    def dumps(self) -> GPXWaypoint:
        """
        Build an XML element for a GPX waypoint.

        Includes identity, geometry and optional comment.
        """
        waypoint = GPXWaypoint(
            latitude=self.latitude, longitude=self.longitude, name=self.identifier, comment=self.comment
        )
        if self.name:
            waypoint.description = self.name
        return waypoint


@dataclass
class RouteWaypoint:
    """Route waypoint for use in a GPX document."""

    waypoint: Waypoint
    comment: str = "-"

    @classmethod
    def loads(cls, route_waypoint: BaseRouteWaypoint) -> Self:
        """Load a base route waypoint as a GPX route waypoint."""
        return RouteWaypoint(waypoint=Waypoint.loads(route_waypoint.waypoint), comment=route_waypoint.waypoint.comment)

    def dumps(self) -> GPXRoutePoint:
        """Build an XML element for a GPX route waypoint."""
        return GPXRoutePoint(
            name=self.waypoint.identifier,
            longitude=self.waypoint.longitude,
            latitude=self.waypoint.latitude,
            comment=self.comment,
        )


@dataclass
class Route:
    """Route for use in a GPX document."""

    name: str | None
    waypoints: list[RouteWaypoint]

    @classmethod
    def loads(cls, route: BaseRoute) -> Self:
        """Load a base route as a GPX route."""
        return Route(name=route.name, waypoints=[RouteWaypoint.loads(rw) for rw in route.waypoints])

    def dumps(self) -> GPXWaypoint:
        """Build an XML element for a GPX route, including rout waypoints."""
        route = GPXRoute(name=self.name)
        for route_waypoint in self.waypoints:
            route.points.append(route_waypoint.dumps())
        return route
