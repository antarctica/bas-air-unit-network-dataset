from __future__ import annotations

import csv
from collections import OrderedDict
from pathlib import Path
from typing import ClassVar, Optional, Union

import ulid
from gpxpy.gpx import GPX, GPXRoute

from bas_air_unit_network_dataset.exporters.fpl.fpl import Fpl
from bas_air_unit_network_dataset.exporters.fpl.route import Route as FplRoute
from bas_air_unit_network_dataset.exporters.fpl.route_waypoint import (
    RouteWaypoint as FplRouteWaypoint,
)
from bas_air_unit_network_dataset.models.route_waypoint import RouteWaypoint
from bas_air_unit_network_dataset.models.waypoint import Waypoint


class Route:
    """
    A known, planned, path between an origin and destination location.

    Routes are containers or namespaces identifying a path that has been pre-planned. Routes themselves only contain an
    identifier and name attribute. The locations that make up the route's path are represented by instances of the
    RouteWaypoint class.

    Routes are templates of paths that can then be followed in a particular journey, each forming a track (and are a
    distinct concept not represented by this library). Routes typically represent regularly travelled paths but this
    isn't required.

    Routes are not spatial features directly, but a linestring geometry can be derived from the point geometry of each
    waypoint associated with the route.

    This class is an abstract representation of a route concept, independent of any specific formats or encodings. It
    includes methods for representing the route and its path - either whole or as origin and destination waypoints.

    See the 'Information Model' section of the library README for more information.
    """

    feature_schema: ClassVar[dict] = {
        "geometry": "None",
        "properties": {"id": "str", "name": "str"},
    }

    feature_schema_spatial: ClassVar[dict] = {
        "geometry": "LineString",
        "properties": {"id": "str", "name": "str"},
    }

    # TODO: Determine why this needs an ordered dict
    # https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/205
    feature_schema_waypoints_spatial: ClassVar[dict] = {
        "geometry": "Point",
        "properties": OrderedDict(),
    }
    feature_schema_waypoints_spatial["properties"]["sequence"] = "int"
    feature_schema_waypoints_spatial["properties"]["identifier"] = "str"
    feature_schema_waypoints_spatial["properties"]["comment"] = "str"

    csv_schema_waypoints: ClassVar[dict] = {
        "sequence": "str",
        "identifier": "str",
        "name": "str",
        "colocated_with": "str",
        "comment": "str",
    }

    def __init__(
        self,
        name: Optional[str] = None,
        route_waypoints: Optional[list[dict[str, Union[str, Waypoint]]]] = None,
    ) -> None:
        """
        Create or load a route, optionally setting parameters.

        Routes will be assigned a unique and persistent feature ID automatically.

        :type name: str
        :param name: optional route name
        :type route_waypoints: list
        :param route_waypoints: optional list of waypoints making up route, wrapped as RouteWaypoint objects
        """
        self._id: str = str(ulid.new())

        self._name: str
        self._waypoints: list[RouteWaypoint] = []

        if name is not None:
            self.name = name

        if route_waypoints is not None:
            self.waypoints = route_waypoints

    @property
    def fid(self) -> str:
        """
        Route feature ID.

        A unique and typically persistent value.

        :rtype: str
        :return: feature ID
        """
        return self._id

    @fid.setter
    def fid(self, _id: str) -> None:
        """
        Set route feature ID.

        This is only intended to be used where an existing route is being loaded, as new routes will be assigned a
        feature ID automatically.

        Typically, a persistent, but otherwise unique, value but which may not be recognisable by humans.

        :type _id: str
        :param _id: feature ID
        """
        self._id = str(ulid.from_str(_id))

    @property
    def name(self) -> str:
        """
        Route name.

        Typically a descriptive value and may not be unique or persistent.

        :rtype: str
        :return: route name
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Set route name.

        Typically a descriptive value. Values are not typically unique or persistent.

        :type name: str
        :param name: route name
        """
        self._name = name

    @property
    def waypoints(self) -> list[RouteWaypoint]:
        """
        Get waypoints that make up route.

        Waypoint will be returned as a RouteWaypoint objects, wrapping around Waypoint objects.

        Typically, there are at least two waypoints, representing a start, end and any intermediate point within the
        route. However, routes may consist of a single waypoint or no waypoints - in which case this property will
        return None.

        :rtype: list
        :return: waypoints that make up route
        """
        return self._waypoints

    @waypoints.setter
    def waypoints(self, route_waypoints: list[RouteWaypoint]) -> None:
        """
        Set waypoints within route.

        Typically, there are at least two waypoints, representing a start and end of the route.

        Waypoints to be added must use the RouteWaypoint class as a wrapper around Waypoint objects.

        Note: Any existing waypoints will be replaced, waypoints will be sorted by their sequence value.

        :type route_waypoints: list
        :param route_waypoints: waypoints that make up route
        """
        # sort route_waypoints by their sequence property
        self._waypoints = sorted(route_waypoints, key=lambda route_waypoint: route_waypoint.sequence)

    @property
    def first_waypoint(self) -> Optional[RouteWaypoint]:
        """
        Get first waypoint in route.

        Typically, this waypoint will be the origin/start of the route. The waypoint will be returned as a RouteWaypoint
        object, wrapping around a Waypoint object.

        Routes may consist of a single waypoint, in which case this property will return the same waypoint as
        `last_waypoint` property.

        Routes may also be empty, with no waypoints, in which case this property will return None.

        :rtype RouteWaypoint
        :return: first waypoint in route wrapped as a RouteWaypoint, if route has waypoints
        """
        try:
            return self.waypoints[0]
        except IndexError:
            return None

    @property
    def last_waypoint(self) -> Optional[RouteWaypoint]:
        """
        Get last waypoint in route.

        Typically, this waypoint will be the destination/end of the route. The waypoint will be returned as a
        RouteWaypoint object, wrapping around a Waypoint object.

        Routes may consist of a single waypoint, in which case this property will return the same waypoint as
        `first_waypoint` property.

        Routes may also be empty, with no waypoints, in which case this property will return None.

        :rtype RouteWaypoint
        :return: last waypoint in route wrapped as a RouteWaypoint, if route has waypoints
        """
        try:
            return self.waypoints[-1]
        except IndexError:
            return None

    @property
    def waypoints_count(self) -> int:
        """
        Number of waypoints that make up route.

        :rtype int
        :return: number of waypoints in route
        """
        return len(self.waypoints)

    def loads_feature(self, feature: dict) -> None:
        """
        Create a Route from a generic feature.

        :type feature: dict
        :param feature: feature representing a Route
        """
        self.fid = feature["properties"]["id"]
        self.name = feature["properties"]["name"]

    def _dumps_feature_route(self, inc_spatial: bool = True) -> dict:
        """
        Build route as a generic feature for further processing.

        :type inc_spatial: bool
        :param inc_spatial: whether to include the geometry of each route in generated feature
        :rtype: dict
        :return: feature for route
        """
        feature = {
            "geometry": None,
            "properties": {"id": self.fid, "name": self.name},
        }

        if inc_spatial:
            geometry = []
            for route_waypoint in self.waypoints:
                geometry.append(route_waypoint.waypoint.dumps_feature_geometry()["coordinates"])
            feature["geometry"] = {"type": "LineString", "coordinates": geometry}

        return feature

    def _dumps_feature_waypoints(
        self,
        inc_spatial: bool = True,
        inc_route_id: bool = False,
        inc_route_name: bool = False,
        use_identifiers: bool = False,
    ) -> list[dict]:
        """
        Build waypoints within route as a set of generic features for further processing.

        :type inc_spatial: bool
        :param inc_spatial: whether to include the geometry of each route waypoint in generated features
        :type inc_route_id: bool
        :param inc_route_id: whether to include the route identifier as an additional feature property
        :type inc_route_name: bool
        :param inc_route_name: whether to include the route name as an additional feature property
        :type use_identifiers: bool
        :param use_identifiers: use waypoint identifiers, rather than FIDs in waypoint features
        :rtype: list
        :return: feature for route waypoints
        """
        _route_id = None
        if inc_route_id:
            _route_id = self.fid

        _route_name = None
        if inc_route_name:
            _route_name = self.name

        features = []
        for route_waypoint in self.waypoints:
            features.append(
                route_waypoint.dumps_feature(
                    inc_spatial=inc_spatial,
                    route_id=_route_id,
                    route_name=_route_name,
                    use_identifiers=use_identifiers,
                )
            )

        return features

    def dumps_feature(
        self,
        inc_spatial: bool = True,
        inc_waypoints: bool = False,
        inc_route_id: bool = False,
        inc_route_name: bool = False,
        use_identifiers: bool = False,
    ) -> Union[dict, list[dict]]:
        """
        Build route as a generic feature for further processing.

        This method returns a feature for the route as a whole if `inc_waypoints=False`, otherwise features are
        generated for each waypoint within the route.

        :type inc_spatial: bool
        :param inc_spatial: whether to include the geometry of the route and/or route waypoints in generated features
        :type inc_waypoints: bool
        :param inc_waypoints: whether to generate a single feature for the route, or features for each route waypoint
        :type inc_route_id: bool
        :param inc_route_id: whether to include the route identifier as an additional feature property
        :type inc_route_name: bool
        :param inc_route_name: whether to include the route name as an additional feature property
        :type use_identifiers: bool
        :param use_identifiers: use waypoint identifiers, rather than FIDs in waypoint features
        :rtype: list / dict
        :return: feature for route or features for route waypoints
        """
        if not inc_waypoints:
            return self._dumps_feature_route(inc_spatial=inc_spatial)

        return self._dumps_feature_waypoints(
            inc_spatial=inc_spatial,
            inc_route_id=inc_route_id,
            inc_route_name=inc_route_name,
            use_identifiers=use_identifiers,
        )

    def dumps_csv(
        self,
        inc_waypoints: bool = False,
        route_column: bool = False,
        inc_dd_lat_lon: bool = True,
        inc_ddm_lat_lon: bool = True,
    ) -> list[dict]:
        """
        Build CSV data for route.

        :type inc_waypoints: bool
        :param inc_waypoints: include waypoints alongside routes
        :type route_column: bool
        :param route_column: include route name as an additional column
        :type inc_dd_lat_lon: bool
        :param inc_dd_lat_lon: include latitude and longitude columns in decimal degree format
        :type inc_ddm_lat_lon: bool
        :param inc_ddm_lat_lon: include latitude and longitude columns in degrees decimal minutes format
        :rtype: list
        :return: rows of generated CSV data for route, a list of dictionaries
        """
        if not inc_waypoints:
            msg = "Routes without waypoints cannot be dumped to CSV, set `inc_waypoints` to True."
            raise RuntimeError(msg)

        csv_rows: list[dict] = []
        for route_waypoint in self.waypoints:
            route_waypoint_csv_row = route_waypoint.dumps_csv(
                inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon
            )

            if route_column:
                route_waypoint_csv_row = {
                    **{"route_name": self.name},
                    **route_waypoint_csv_row,
                }

            csv_rows.append(route_waypoint_csv_row)

        return csv_rows

    def dump_csv(
        self,
        path: Path,
        inc_waypoints: bool = False,
        route_column: bool = False,
        inc_dd_lat_lon: bool = True,
        inc_ddm_lat_lon: bool = True,
    ) -> None:
        """
        Write route as a CSV file for further processing and/or visualisation.

        Wrapper around `dumps_csv()` method.

        :type path: Path
        :param path: base path for exported files
        :type inc_waypoints: bool
        :param inc_waypoints: include waypoints alongside routes
        :type route_column: bool
        :param route_column: include route name as an additional column
        :type inc_dd_lat_lon: bool
        :param inc_dd_lat_lon: include latitude and longitude columns in decimal degree format
        :type inc_ddm_lat_lon: bool
        :param inc_ddm_lat_lon: include latitude and longitude columns in degrees decimal minutes format
        """
        # this process is very inelegant and needs improving to remove duplication [#110]
        fieldnames: list[str] = list(Route.csv_schema_waypoints.keys())
        if inc_dd_lat_lon:
            fieldnames = [
                "sequence",
                "identifier",
                "name",
                "colocated_with",
                "latitude_dd",
                "longitude_dd",
                "last_accessed_at",
                "last_accessed_by",
                "comment",
            ]
        if inc_ddm_lat_lon:
            fieldnames = [
                "sequence",
                "identifier",
                "name",
                "colocated_with",
                "latitude_ddm",
                "longitude_ddm",
                "last_accessed_at",
                "last_accessed_by",
                "comment",
            ]
        if inc_dd_lat_lon and inc_ddm_lat_lon:
            fieldnames = [
                "sequence",
                "identifier",
                "name",
                "colocated_with",
                "latitude_dd",
                "longitude_dd",
                "latitude_ddm",
                "longitude_ddm",
                "last_accessed_at",
                "last_accessed_by",
                "comment",
            ]

        if route_column:
            fieldnames = ["route_name", *fieldnames]

        # newline parameter needed to avoid extra blank lines in files on Windows [#63]
        with path.open(mode="w", newline="", encoding="utf-8-sig") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(
                self.dumps_csv(
                    inc_waypoints=inc_waypoints,
                    route_column=route_column,
                    inc_dd_lat_lon=inc_dd_lat_lon,
                    inc_ddm_lat_lon=inc_ddm_lat_lon,
                )
            )

    def dumps_gpx(self, inc_waypoints: bool = False) -> GPX:
        """
        Build a GPX document for route.

        :type inc_waypoints: bool
        :param inc_waypoints: include waypoints in generated document
        :rtype: GPX
        :return: generated GPX file for route
        """
        gpx = GPX()
        route = GPXRoute()

        route.name = self.name

        for route_waypoint in self.waypoints:
            route.points.append(route_waypoint.dumps_gpx())

            if inc_waypoints:
                gpx.waypoints.append(route_waypoint.waypoint.dumps_gpx())

        gpx.routes.append(route)

        return gpx

    def dump_gpx(self, path: Path, inc_waypoints: bool = False) -> None:
        """
        Write route as a GPX file for use in GPS devices.

        :type path: Path
        :param path: base path for exported files
        :type inc_waypoints: bool
        :param inc_waypoints: include waypoints alongside routes
        """
        with path.open(mode="w") as gpx_file:
            gpx_file.write(self.dumps_gpx(inc_waypoints=inc_waypoints).to_xml())

    def dumps_fpl(self, flight_plan_index: int) -> Fpl:
        """
        Build a FPL document for route.

        The FPL standard uses an index value to distinguish different routes, rather than route or file names. Index
        values must therefore be unique between 0 and 98. See the FPL exporter class for more information.

        :type flight_plan_index: int
        :param flight_plan_index: FPL index
        :rtype: Fpl
        :return: generated FPL for route
        """
        fpl = Fpl()
        route = FplRoute()

        route.name = self.name
        route.index = flight_plan_index

        for route_waypoint in self.waypoints:
            route_point = FplRouteWaypoint()
            route_point.waypoint_reference = route_waypoint.waypoint.identifier
            route_point.waypoint_type = "USER WAYPOINT"
            route_point.waypoint_country_code = "__"
            route.points.append(route_point)

        fpl.route = route
        fpl.validate()

        return fpl

    def dump_fpl(self, path: Path, flight_plan_index: int) -> None:
        """
        Write route as a Garmin FPL file for use in aircraft GPS devices.

        Wrapper around `dumps_fpl()` method.

        :type path: path
        :param path: Output path
        :type flight_plan_index: int
        :param flight_plan_index: FPL index
        """
        with path.open(mode="w") as xml_file:
            xml_file.write(self.dumps_fpl(flight_plan_index=flight_plan_index).dumps_xml().decode())

    def __repr__(self) -> str:
        """Represent Route as a string."""
        start = "-"
        end = "-"

        try:
            start = self.first_waypoint.waypoint.identifier.ljust(6)
            end = self.last_waypoint.waypoint.identifier.ljust(6)
        except AttributeError:
            pass

        return f"<Route {self.fid} :- [{self.name.ljust(10, '_')}], {self.waypoints_count} waypoints, Start/End: {start} / {end}>"
