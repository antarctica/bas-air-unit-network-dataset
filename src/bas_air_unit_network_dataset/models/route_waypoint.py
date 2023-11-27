from __future__ import annotations

from typing import ClassVar, Optional

from gpxpy.gpx import GPXRoutePoint

from bas_air_unit_network_dataset.models.waypoint import Waypoint
from bas_air_unit_network_dataset.models.waypoints import WaypointCollection


class RouteWaypoint:
    """
    A Waypoint within a Route.

    Route waypoints link a particular Waypoint to a particular Route, including contextual information on where with
    the route a waypoint appears (i.e. at the beginning, end or somewhere inbetween).

    This class handles singular waypoints/positions within a route. All waypoints and positions within a route are
    managed by the Route class.

    See the 'Information Model' section of the library README for more information.
    """

    feature_schema: ClassVar[dict] = {
        "geometry": "None",
        "properties": {"route_id": "str", "waypoint_id": "str", "sequence": "int"},
    }

    feature_schema_spatial: ClassVar[dict] = {
        "geometry": "Point",
        "properties": feature_schema["properties"],
    }

    def __init__(self, waypoint: Optional[Waypoint] = None, sequence: Optional[int] = None) -> None:
        """
        Create or load a routes, optionally setting parameters.

        :type waypoint: Waypoint
        :param waypoint: the Waypoint that forms part of the Route Waypoint
        :type sequence: int
        :param sequence: order of waypoint in route
        """
        self._waypoint: Waypoint
        self._sequence: int

        if waypoint is not None and sequence is None:
            msg = "A `sequence` value must be provided if `waypoint` is set."
            raise ValueError(msg)
        if waypoint is None and sequence is not None:
            msg = "A `waypoint` value must be provided if `sequence` is set."
            raise ValueError(msg)

        if waypoint is not None:
            self.waypoint = waypoint
        if sequence is not None:
            self.sequence = sequence

    @property
    def waypoint(self) -> Waypoint:
        """
        Waypoint.

        :rtype: Waypoint
        :return: the Waypoint that forms part of the Route Waypoint
        """
        return self._waypoint

    @waypoint.setter
    def waypoint(self, waypoint: Waypoint) -> None:
        """
        Set waypoint.

        :type waypoint: Waypoint
        :param waypoint: the Waypoint that forms part of the Route Waypoint
        """
        self._waypoint = waypoint

    @property
    def sequence(self) -> int:
        """
        Order of waypoint within route.

        Waypoints in routes are ordered (from start to end) using a sequence order (ascending order).

        :rtype: int
        :return: order of waypoint in route
        """
        return self._sequence

    @sequence.setter
    def sequence(self, sequence: int) -> None:
        """
        Set order of waypoint within route.

        Waypoints in routes are ordered (from start to end) using a sequence order (ascending order).

        :type sequence: int
        :param sequence: order of waypoint in route
        """
        self._sequence = sequence

    def loads_feature(self, feature: dict, waypoints: WaypointCollection) -> None:
        """
        Create a route waypoint from a generic feature.

        Route Waypoint features contain a reference to a Waypoint rather than embedding the entire Waypoint. Recreating
        the Route Waypoint therefore requires a list of Waypoints to load additional information from.

        :type feature: dict
        :param feature: feature representing a Route Waypoint
        :type waypoints: WaypointCollection
        :param waypoints: collection of waypoints from which to load waypoint information
        """
        self.sequence = feature["properties"]["sequence"]

        try:
            self.waypoint = waypoints[feature["properties"]["waypoint_id"]]
        except KeyError as e:
            msg = f"Waypoint with ID {feature['properties']['waypoint_id']!r} not found in available waypoints."
            raise KeyError(msg) from e

    def dumps_feature(
        self,
        inc_spatial: bool = True,
        route_id: Optional[str] = None,
        route_name: Optional[str] = None,
        use_identifiers: bool = False,
    ) -> dict:
        """
        Build route waypoint as a generic feature for further processing.

        :type inc_spatial: bool
        :param inc_spatial: whether to include the geometry of the route and/or route waypoints in generated features
        :type route_id: str
        :param route_id: optional value to use for route identifier as an additional feature property
        :type route_name: str
        :param route_name: optional value to use for route name as an additional feature property
        :type use_identifiers: bool
        :param use_identifiers: use waypoint identifiers, rather than FIDs in waypoint features
        :rtype: dict
        :return: feature for route waypoint
        """
        feature = {
            "geometry": None,
            "properties": {"waypoint_id": self.waypoint.fid, "sequence": self.sequence},
        }

        if inc_spatial:
            geometry = {
                "type": "Point",
                "coordinates": (self.waypoint.geometry.x, self.waypoint.geometry.y),
            }
            if self.waypoint.geometry.has_z:
                geometry["coordinates"] = (
                    self.waypoint.geometry.x,
                    self.waypoint.geometry.y,
                    self.waypoint.geometry.z,
                )
            feature["geometry"] = geometry

        if use_identifiers:
            del feature["properties"]["waypoint_id"]
            feature["properties"] = {
                **{"identifier": self.waypoint.identifier},
                **feature["properties"],
            }

        if route_name is not None:
            feature["properties"] = {
                **{"route_name": route_name},
                **feature["properties"],
            }

        if route_id is not None:
            feature["properties"] = {**{"route_id": route_id}, **feature["properties"]}

        return feature

    def dumps_csv(self, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> dict[str, str]:
        """
        Build CSV data for route waypoint.

        :type inc_dd_lat_lon: bool
        :param inc_dd_lat_lon: include latitude and longitude columns in decimal degree format
        :type inc_ddm_lat_lon: bool
        :param inc_ddm_lat_lon: include latitude and longitude columns in degrees decimal minutes format
        :rtype: dict
        :return: row of generated CSV data for route waypoint
        """
        route_waypoint = {"sequence": self.sequence}

        waypoint = self.waypoint.dumps_csv(inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon)
        del waypoint["comment"]
        del waypoint["last_accessed_at"]
        del waypoint["last_accessed_by"]

        return {**route_waypoint, **waypoint}

    def dumps_gpx(self) -> GPXRoutePoint:
        """
        Build GPX element for route waypoint.

        :rtype: GPXRoutePoint
        :return: generated GPX element for route waypoint
        """
        route_waypoint = GPXRoutePoint()
        route_waypoint.name = self.waypoint.identifier
        route_waypoint.longitude = self.waypoint.geometry.x
        route_waypoint.latitude = self.waypoint.geometry.y
        route_waypoint.comment = self.waypoint.comment

        return route_waypoint
