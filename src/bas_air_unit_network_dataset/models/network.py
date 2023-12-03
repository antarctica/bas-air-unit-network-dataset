from __future__ import annotations

from pathlib import Path
from typing import Optional

from gpxpy import parse as gpx_parse
from gpxpy.gpx import GPX, GPXRoute

from bas_air_unit_network_dataset.models.route import Route
from bas_air_unit_network_dataset.models.route_waypoint import RouteWaypoint
from bas_air_unit_network_dataset.models.routes import RouteCollection
from bas_air_unit_network_dataset.models.waypoints import WaypointCollection


class Network:
    """
    A collection of Waypoints and Routes.

    A network is a logical set of Waypoints and Routes for a given purpose or context. For example, a global or
    regional logistics network, a science project, etc.

    The Network class provides a waypoints and route collection, along with methods for loading and dumping features at
    a network level. This class will typically be extended to use specific naming conventions or to construct custom
    outputs as needed.
    """

    def __init__(
        self, waypoints: Optional[WaypointCollection] = None, routes: Optional[RouteCollection] = None
    ) -> None:
        self._waypoints: WaypointCollection = WaypointCollection()
        self._routes: RouteCollection = RouteCollection()

        if waypoints is not None:
            self.waypoints = waypoints
        if routes is not None:
            self.routes = routes

    @property
    def waypoints(self) -> WaypointCollection:
        """
        Waypoints.

        Waypoints in this network.

        :rtype: WaypointCollection
        :return: network waypoints
        """
        return self._waypoints

    @waypoints.setter
    def waypoints(self, waypoints: WaypointCollection) -> None:
        self._waypoints = waypoints

    @property
    def routes(self) -> RouteCollection:
        """
        Routes.

        Routes in this network.

        :rtype: RouteCollection
        :return: network routes
        """
        return self._routes

    @routes.setter
    def routes(self, routes: RouteCollection) -> None:
        self._routes = routes

    def _load_gpx_routes(self, gpx_routes: list[GPXRoute]) -> None:
        """
        Read routes from GPX data.

        :type gpx_routes: list[GPXRoute]
        :param gpx_routes: list of GPX routes
        """
        for gpx_route in gpx_routes:
            route = Route()
            route.name = gpx_route.name

            sequence = 1
            for route_waypoint in gpx_route.points:
                waypoint = self.waypoints.lookup(route_waypoint.name)

                route_waypoint = RouteWaypoint(waypoint=waypoint, sequence=sequence)
                route.waypoints.append(route_waypoint)
                sequence += 1

            self.routes.append(route)

    def display(self) -> None:
        """
        Display information about a network.

        Prints to stdout, formatted for use in a CLI.
        """
        waypoints_zfill = len(str(len(self.waypoints)))
        routes_zfill = len(str(len(self.routes)))

        print(self)
        print("")

        print(f"Waypoints [{len(self.waypoints)}]:")
        for i, waypoint in enumerate(self.waypoints):
            print(f"{str(i + 1).zfill(waypoints_zfill)}. {waypoint}")
        print("")

        print(f"Routes [{len(self.routes)}]:")
        for i, route in enumerate(self.routes):
            print(f"{str(i + 1).zfill(routes_zfill)}. {route}")

    def load_gpx(self, path: Path) -> None:
        """
        Read routes and waypoints from a GPX file.

        :type path: Path
        :param path: input GPX file path
        """
        with path.open(mode="r", encoding="utf-8-sig") as gpx_file:
            gpx_data = gpx_parse(gpx_file)
            self.waypoints.loads_gpx(gpx_waypoints=gpx_data.waypoints)
            self._load_gpx_routes(gpx_routes=gpx_data.routes)

    def dump_gpx(self, path: Path) -> None:
        """
        Write network wide GPX file for use in GPS devices.

        Contains all routes and waypoints.

        :type path: Path
        :param path: output GPX file path
        """
        gpx = GPX()
        gpx.waypoints = self.waypoints.dumps_gpx().waypoints
        gpx.routes = self.routes.dumps_gpx().routes

        with path.open(mode="w") as gpx_file:
            gpx_file.write(gpx.to_xml())

    def __repr__(self) -> str:
        """Representation of Network as a string."""
        return f"<Network : {len(self.waypoints)} Waypoints - {len(self.routes)} Routes>"
