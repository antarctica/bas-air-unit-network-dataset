from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path

from gpxpy.gpx import GPX

from bas_air_unit_network_dataset.models.route import Route


class RouteCollection:
    """
    A collection of Routes.

    Provides a dictionary like interface to managing Routes, along with methods for managing multiple Routes at once.
    """

    def __init__(self) -> None:
        """Create routes collection."""
        self._routes: list[Route] = []

    @property
    def routes(self) -> list[Route]:
        """
        Get all routes in collection as Route classes.

        :rtype: list
        :return: routes in collection as Route classes
        """
        return self._routes

    def append(self, route: Route) -> None:
        """
        Add route to collection.

        :type route: Route
        :param route: additional route
        """
        self._routes.append(route)

    def dumps_features(
        self,
        inc_spatial: bool = True,
        inc_waypoints: bool = False,
        inc_route_id: bool = False,
        inc_route_name: bool = False,
    ) -> list[dict]:
        """
        Build all routes in collection as generic features for further processing.

        This method is a wrapper around the `dumps_feature()` method for each route.

        :type inc_spatial: bool
        :param inc_spatial: whether to include the geometry of each route in generated features
        :type inc_waypoints: bool
        :param inc_waypoints: whether to generate a single feature for the route, or features for each route waypoint
        :type inc_route_id: bool
        :param inc_route_id: whether to include the route identifier as an additional feature property
        :type inc_route_name: bool
        :param inc_route_name: whether to include the route name as an additional feature property
        :rtype: list
        :return: features for routes or route waypoints, for each route in collection
        """
        features = []

        for route in self.routes:
            if not inc_waypoints:
                features.append(route.dumps_feature(inc_spatial=inc_spatial, inc_waypoints=False))
                continue
            features += route.dumps_feature(
                inc_spatial=inc_spatial,
                inc_waypoints=True,
                inc_route_id=inc_route_id,
                inc_route_name=inc_route_name,
            )

        return features

    def _dump_csv_separate(self, path: Path, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> None:
        """
        Write each route as a CSV file for further processing and/or visualisation.

        Files and directories currently use BAS Air Unit specific naming conventions - this will be addressed in #46.

        :type path: Path
        :param path: base path for exported files
        :type inc_dd_lat_lon: bool
        :param inc_dd_lat_lon: include latitude and longitude columns in decimal degree format
        :type inc_ddm_lat_lon: bool
        :param inc_ddm_lat_lon: include latitude and longitude columns in degrees decimal minutes format
        """
        for route in self.routes:
            route.dump_csv(
                path=path.joinpath(f"{route.name.upper()}.csv"),
                inc_waypoints=True,
                route_column=False,
                inc_dd_lat_lon=inc_dd_lat_lon,
                inc_ddm_lat_lon=inc_ddm_lat_lon,
            )

    def _dump_csv_combined(self, path: Path, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> None:
        """
        Write all routes to a single CSV file for further processing and/or visualisation.

        :type path: path
        :param path: Output path
        :type inc_dd_lat_lon: bool
        :param inc_dd_lat_lon: include latitude and longitude columns in decimal degree format
        :type inc_ddm_lat_lon: bool
        :param inc_ddm_lat_lon: include latitude and longitude columns in degrees decimal minutes format
        """
        fieldnames: list[str] = ["route_name", *list(Route.csv_schema_waypoints.keys())]

        route_waypoints: list[dict] = []
        for route in self.routes:
            route_waypoints += route.dumps_csv(
                inc_waypoints=True,
                route_column=True,
                inc_dd_lat_lon=inc_dd_lat_lon,
                inc_ddm_lat_lon=inc_ddm_lat_lon,
            )

        # newline parameter needed to avoid extra blank lines in files on Windows [#63]
        with path.open(mode="w", newline="", encoding="utf-8-sig") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(route_waypoints)

    def dump_csv(
        self,
        path: Path,
        separate_files: bool = False,
        inc_dd_lat_lon: bool = False,
        inc_ddm_lat_lon: bool = False,
    ) -> None:
        """
        Write routes as CSV files for further processing and/or visualisation.

        :type path: Path
        :param path: base path for exported files
        :type separate_files: bool
        :param separate_files: generate separate files per route
        :type inc_dd_lat_lon: bool
        :param inc_dd_lat_lon: include latitude and longitude columns in decimal degree format
        :type inc_ddm_lat_lon: bool
        :param inc_ddm_lat_lon: include latitude and longitude columns in degrees decimal minutes format
        """
        if separate_files:
            self._dump_csv_separate(
                path=path,
                inc_dd_lat_lon=inc_dd_lat_lon,
                inc_ddm_lat_lon=inc_ddm_lat_lon,
            )
        else:
            self._dump_csv_combined(
                path=path,
                inc_dd_lat_lon=inc_dd_lat_lon,
                inc_ddm_lat_lon=inc_ddm_lat_lon,
            )

    def dumps_gpx(self, inc_waypoints: bool = False) -> GPX:
        """
        Build a GPX document for route within collection.

        :type inc_waypoints: bool
        :param inc_waypoints: include waypoints in generated document
        :rtype: GPX
        :return: generated GPX file containing all routes in collection
        """
        gpx = GPX()
        _waypoints = []

        for route in self.routes:
            gpx.routes.append(route.dumps_gpx(inc_waypoints=False).routes[0])

            if inc_waypoints:
                _waypoints += route.dumps_gpx(inc_waypoints=True).waypoints

        if inc_waypoints:
            gpx.waypoints = _waypoints

        return gpx

    def _dump_gpx_separate(self, path: Path, inc_waypoints: bool = False) -> None:
        """
        Write each route as a GPX file for use in GPS devices.

        Files and directories currently use BAS Air Unit specific naming conventions - this will be addressed in #46.

        :type path: Path
        :param path: base path for exported files
        :type inc_waypoints: bool
        :param inc_waypoints: include waypoints alongside routes
        """
        for route in self.routes:
            route.dump_gpx(
                path=path.joinpath(f"{route.name.upper()}.gpx"),
                inc_waypoints=inc_waypoints,
            )

    def _dump_gpx_combined(self, path: Path) -> None:
        """
        Write all routes to a single GPX file for use in GPS devices.

        :type path: path
        :param path: Output path
        """
        with path.open(mode="w") as gpx_file:
            gpx_file.write(self.dumps_gpx().to_xml())

    def dump_gpx(self, path: Path, separate_files: bool = False, inc_waypoints: bool = False) -> None:
        """
        Write routes as GPX files for use in GPS devices.

        Files and directories currently use BAS Air Unit specific naming conventions - this will be addressed in #46.

        :type path: Path
        :param path: base path for exported files
        :type separate_files: bool
        :param separate_files: generate separate files per route
        :type inc_waypoints: bool
        :param inc_waypoints: include waypoints alongside routes
        """
        if separate_files:
            self._dump_gpx_separate(path=path, inc_waypoints=inc_waypoints)
            return

        self._dump_gpx_combined(path=path)

    def dump_fpl(self, path: Path, separate_files: bool = False) -> None:
        """
        Write routes as Garmin FPL files for use in aircraft GPS devices.

        This method is a wrapper around the `dump_fpl()` method for each route (FPL doesn't support combined routes).

        Route collections are assumed to be exclusive, with each route assigned a flight plan index corresponding to its
        insert order, starting from `1`. I.e. the third route added to the collection has an index of `3`.

        Files and directories currently use BAS Air Unit specific naming conventions - this will be addressed in #46.

        :type path: Path
        :param path: base path for exported files
        :type separate_files: bool
        :param separate_files: generate separate files per route
        """
        if not separate_files:
            msg = "FPL does not support combined routes, `separate_files` must be set to True."
            raise RuntimeError(msg)

        flight_plan_index = 1
        for route in self.routes:
            route.dump_fpl(
                path=path.joinpath(f"{route.name.upper()}.fpl"),
                flight_plan_index=flight_plan_index,
            )
            flight_plan_index += 1

    def __getitem__(self, _id: str) -> Route:
        """
        Get a Route by its ID.

        :type _id: Route
        :param _id: a route ID (distinct from a route's Identifier)
        :rtype Route
        :return: specified Route

        :raises KeyError: if no route exists with the requested ID
        """
        for route in self.routes:
            if route.fid == _id:
                return route

        raise KeyError(_id)

    def __iter__(self) -> Iterator[Route]:
        """Iterate through each Route within RouteCollection."""
        return self.routes.__iter__()

    def __len__(self) -> int:
        """Routes in RouteCollection."""
        return len(self.routes)

    def __repr__(self) -> str:
        """Represent RouteCollection as a string."""
        return f"<RouteCollection : {self.__len__()} routes>"
