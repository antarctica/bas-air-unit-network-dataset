from datetime import datetime
from typing import Optional, List, Dict, Iterator

from shapely.geometry import Point
import ulid


class Waypoint:
    designator_max_length = 6

    def __init__(
        self,
        designator: str,
        lon: float,
        lat: float,
        alt: Optional[float] = None,
        comment: Optional[str] = None,
        last_accessed_at: Optional[datetime] = None,
        last_accessed_by: Optional[str] = None,
    ) -> None:
        self.id: str = self._make_id()
        self.designator: str = designator
        self.geometry: Point = Point(lon, lat)
        self.comment: str = comment
        self.last_accessed_at: datetime = last_accessed_at
        self.last_accessed_by: str = last_accessed_by

        if len(designator) > Waypoint.designator_max_length:
            raise ValueError(f"Designators must be 6 characters or less. '{designator}' is {len(designator)}.")

        if lon < -180 or lon > 180:
            raise ValueError(f"Invalid Longitude, must be -180<=X<=180 not {lon}.")
        if lat < -90 or lat > 90:
            raise ValueError(f"Invalid Latitude, must be -90<=Y<=+90 not {lat}.")

        if alt is not None:
            self.geometry = Point(lon, lat, alt)

        if last_accessed_at is not None and last_accessed_by is None:
            raise ValueError("A `last_accessed_by` value must be provided if `last_accessed_at` is set.")
        if last_accessed_at is None and last_accessed_by is not None:
            raise ValueError("A `last_accessed_at` value must be provided if `last_accessed_by` is set.")

    @staticmethod
    def _make_id() -> str:
        return str(ulid.new())

    def __repr__(self) -> str:
        return f"<Waypoint {self.id} :- [{self.designator.ljust(6, '_')}], {self.geometry}>"


class RouteWaypoint:
    def __init__(self, waypoint: Waypoint, sequence: int, description: Optional[str] = None) -> None:
        self.waypoint: Waypoint = waypoint
        self.description: str = description
        self.sequence: int = sequence


class Route:
    def __init__(
        self,
        name: str,
        route_waypoints: List[Dict[str, str]],
        waypoints: "WaypointCollection",
    ) -> None:
        self.id: str = self._make_id()
        self.name: str = name
        self.waypoints: List[RouteWaypoint] = self._process_waypoints(
            route_waypoints=route_waypoints, waypoints=waypoints
        )

    @staticmethod
    def _make_id() -> str:
        return str(ulid.new())

    @staticmethod
    def _process_waypoints(
        route_waypoints: List[Dict[str, str]], waypoints: "WaypointCollection"
    ) -> List[RouteWaypoint]:
        sequence = 1
        _waypoints: List[RouteWaypoint] = []

        for route_waypoint in route_waypoints:
            try:
                waypoint = waypoints.get_by_designator(designator=route_waypoint["waypoint_designator"])
            except IndexError:
                raise IndexError(
                    f"Waypoint with designator '{route_waypoint['waypoint_designator']}' not found in available waypoints."
                )

            try:
                _description = route_waypoint["description"]
            except KeyError:
                _description = None

            _waypoints.append(
                RouteWaypoint(
                    waypoint=waypoint,
                    sequence=sequence,
                    description=_description,
                )
            )
            sequence += 1

        return _waypoints

    @property
    def first_waypoint(self) -> RouteWaypoint:
        return self.waypoints[0]

    @property
    def last_waypoint(self) -> RouteWaypoint:
        return self.waypoints[-1]

    @property
    def waypoints_count(self) -> int:
        return len(self.waypoints)

    def __repr__(self) -> str:
        return (
            f"<Route {self.id} :- [{self.name.ljust(10, '_')}], {self.waypoints_count} waypoints, Start/End: "
            f"{self.first_waypoint.waypoint.designator.ljust(6)} / {self.last_waypoint.waypoint.designator.ljust(6)}>"
        )


class WaypointCollection:
    def __init__(self) -> None:
        self._waypoints: List[Waypoint] = []

    def append(self, waypoint: Waypoint) -> None:
        self._waypoints.append(waypoint)

    @property
    def count(self) -> int:
        return len(self._waypoints)

    def get_by_designator(self, designator: str) -> Waypoint:
        for waypoint in self._waypoints:
            if waypoint.designator == designator:
                return waypoint

        raise IndexError(f"Waypoint with designator '{designator}' not found.")

    def __iter__(self) -> Iterator:
        return self._waypoints.__iter__()

    def __repr__(self) -> str:
        return f"<WaypointCollection : {self.count} waypoints>"


class RouteCollection:
    def __init__(self) -> None:
        self._routes: List[Route] = []

    def append(self, route: Route) -> None:
        self._routes.append(route)

    @property
    def count(self) -> int:
        return len(self._routes)

    def __iter__(self) -> Iterator:
        return self._routes.__iter__()

    def __repr__(self) -> str:
        return f"<RouteCollection : {self.count} routes>"


class NetworkManager:
    # If you can come up with a better name for this class, you could win a prize!

    def __init__(self):
        self.waypoints: WaypointCollection = WaypointCollection()
        self.routes: RouteCollection = RouteCollection()

    def __repr__(self):
        return f"<NetworkManager : {self.waypoints.count} Waypoints - {self.routes.count} Routes>"
