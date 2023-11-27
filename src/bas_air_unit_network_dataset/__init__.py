from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import fiona
from fiona.crs import from_epsg as crs_from_epsg
from gpxpy import parse as gpx_parse
from gpxpy.gpx import GPX

from bas_air_unit_network_dataset.models.route import Route
from bas_air_unit_network_dataset.models.route_waypoint import RouteWaypoint
from bas_air_unit_network_dataset.models.routes import RouteCollection
from bas_air_unit_network_dataset.models.waypoint import Waypoint
from bas_air_unit_network_dataset.models.waypoints import WaypointCollection
from bas_air_unit_network_dataset.utils import file_name_with_date


class NetworkManager:
    """
    A collection of Routes and Waypoints that form a network.

    It provides methods for importing and exporting route and waypoint information in various formats using a
    defined file naming and directory structure, which is specific to the BAS Air Unit.
    """

    def __init__(
        self,
        dataset_path: Path,
        output_path: Optional[Path] = None,
        init: Optional[bool] = False,
    ) -> None:
        """
        Create or load a network of waypoints and routes, optionally setting parameters.

        :type dataset_path: Path
        :param dataset_path: file path to GeoPackage used for data persistence
        :type output_path: Path
        :param output_path: base path to use for output files
        :type init: bool
        :param init: create a new network if one does not exist
        """
        self.waypoints: WaypointCollection = WaypointCollection()
        self.routes: RouteCollection = RouteCollection()

        if init:
            # GDAL/Fiona doesn't create missing parent directories
            dataset_path.parent.mkdir(parents=True, exist_ok=True)
            self._dump_gpkg(path=dataset_path)

        self.dataset_path = dataset_path
        self._load_gpkg(path=self.dataset_path)

        self.output_path: Optional[Path] = None
        if output_path is not None:
            if not dataset_path.exists():
                msg = "Output path does not exist."
                raise FileNotFoundError(msg)
            self.output_path = output_path

    def _get_output_path(self, path: Optional[Path], fmt_dir: Optional[str] = None) -> Path:
        """
        Generate and run basic tests on a path for an output file.

        This method takes a file format name as output paths are typically grouped (contained) by file type.

        running basic checks
        :type path: Path
        :param path: output file path
        :type fmt_dir: str
        :param fmt_dir: optional file format
        :rtype: path
        :return: generated and validated file path
        """
        if path is None and self.output_path is not None:
            path = self.output_path

        if path is None:
            msg = "No output path specified"
            raise FileNotFoundError(msg)

        path = path.resolve()
        if fmt_dir is not None:
            path = path.joinpath(fmt_dir)

        path.mkdir(parents=True, exist_ok=True)

        if not path.exists():
            msg = "Output path does not exist."
            raise FileNotFoundError(msg)

        return path

    def _load_gpkg(self, path: Optional[Path] = None) -> None:
        """
        Read routes and waypoints from a GeoPackage as part of data persistence.

        That GeoPackages are used for persisting information is an implementation detail internal to this library. It
        isn't a file format intended for use by end-users, and this is therefore an internal method.

        As the GeoPackage is a flexible format, it reflects the internal structure of and collections used by this
        class without easing parsing.

        :type path: Path
        :param path: Input file
        """
        # waypoints
        with fiona.open(path, mode="r", driver="GPKG", layer="waypoints") as layer:
            for waypoint_feature in layer:
                waypoint = Waypoint()
                waypoint.loads_feature(feature=waypoint_feature)
                self.waypoints.append(waypoint)

        # routes & route-waypoints
        with fiona.open(path, mode="r", driver="GPKG", layer="routes") as layer:
            for route_feature in layer:
                route = Route()
                route.loads_feature(feature=route_feature)
                self.routes.append(route)
        with fiona.open(path, mode="r", driver="GPKG", layer="route_waypoints") as layer:
            # process route waypoints and group by route
            route_waypoints_by_route_id: dict[str, list[RouteWaypoint]] = {}
            for route_waypoint_feature in layer:
                route_waypoint = RouteWaypoint()
                route_waypoint.loads_feature(feature=route_waypoint_feature, waypoints=self.waypoints)

                if route_waypoint_feature["properties"]["route_id"] not in route_waypoints_by_route_id:
                    route_waypoints_by_route_id[route_waypoint_feature["properties"]["route_id"]] = []
                route_waypoints_by_route_id[route_waypoint_feature["properties"]["route_id"]].append(route_waypoint)

            for (
                route_id,
                route_waypoint_features,
            ) in route_waypoints_by_route_id.items():
                route = self.routes[route_id]
                route.waypoints = route_waypoint_features

    def _dump_gpkg(self, path: Path) -> None:
        """
        Write routes and waypoints to a GeoPackage for data persistence.

        That GeoPackages are used for persisting information is an implementation detail internal to this library. It
        isn't a file format intended for use by end-users, and this is therefore an internal method.

        As the GeoPackage is a flexible format, it can be used to reflect the internal structure of and collections used
        by this class without any shuffling or serialisation.

        :type path: Path
        :param path: Output file
        """
        # waypoints
        with fiona.open(
            path,
            mode="w",
            driver="GPKG",
            crs=crs_from_epsg(4326),
            schema=Waypoint.feature_schema_spatial,
            layer="waypoints",
        ) as layer:
            layer.writerecords(self.waypoints.dump_features(inc_spatial=True))

        # route_waypoints
        with fiona.open(
            path,
            mode="w",
            driver="GPKG",
            schema=RouteWaypoint.feature_schema,
            layer="route_waypoints",
        ) as layer:
            layer.writerecords(self.routes.dumps_features(inc_spatial=False, inc_waypoints=True, inc_route_id=True))

        # routes
        with fiona.open(
            path,
            mode="w",
            driver="GPKG",
            crs=crs_from_epsg(4326),
            schema=Route.feature_schema,
            layer="routes",
        ) as layer:
            layer.writerecords(self.routes.dumps_features(inc_spatial=False, inc_waypoints=False))

    def load_gpx(self, path: Path) -> None:
        """
        Read routes and waypoints from a GPX file.

        This method parses any routes and/or waypoints from the input file, updating collections in this class and
        persisting the data to the configured GeoPackage.

        :type path: Path
        :param path: input GPX file path
        """
        with path.open(mode="r", encoding="utf-8-sig") as gpx_file:
            gpx_data = gpx_parse(gpx_file)

        # waypoints
        for waypoint in gpx_data.waypoints:
            _waypoint = Waypoint()
            _waypoint.identifier = waypoint.name
            _waypoint.geometry = [waypoint.longitude, waypoint.latitude]

            if waypoint.description is not None and waypoint.description != "N/A | N/A | N/A | N/A | N/A":
                comment_elements = waypoint.description.split("|")
                name = comment_elements[0].strip()
                colocated_with = comment_elements[1].strip()
                last_accessed_at = comment_elements[2].strip()
                last_accessed_by = comment_elements[3].strip()
                comment = comment_elements[4].strip()

                if name != "N/A":
                    _waypoint.name = name
                if colocated_with != "N/A":
                    _waypoint.colocated_with = colocated_with
                if last_accessed_at != "N/A":
                    _waypoint.last_accessed_at = date.fromisoformat(last_accessed_at)
                if last_accessed_by != "N/A":
                    _waypoint.last_accessed_by = last_accessed_by
                if comment != "N/A":
                    _waypoint.comment = comment

            self.waypoints.append(_waypoint)

        # routes & route-waypoints
        for route in gpx_data.routes:
            _route = Route()
            _route.name = route.name

            sequence = 1
            for route_waypoint in route.points:
                _waypoint = self.waypoints.lookup(route_waypoint.name)

                _route_waypoint = RouteWaypoint(waypoint=_waypoint, sequence=sequence)
                _route.waypoints.append(_route_waypoint)
                sequence += 1

            self.routes.append(_route)

        # once data is loaded, save to GeoPackage
        self._dump_gpkg(path=self.dataset_path)

    def dump_csv(self, path: Optional[Path] = None) -> None:
        """
        Write routes and waypoints as CSV files for further processing and/or visualisation.

        This method is a wrapper around the `dump_csv()` methods for routes and waypoints.

        Files and directories currently use BAS Air Unit specific naming conventions - this will be addressed in #46.

        A CSV file containing all routes and each individual route would normally be generated, but as they are not
        needed by BAS Air Unit they are currently disabled - this will be addressed in #46.

        :type path: Path
        :param path: base path for exported files
        """
        path = self._get_output_path(path=path, fmt_dir="CSV")

        self.waypoints.dump_csv(
            path=path.joinpath(file_name_with_date("00_WAYPOINTS_DDM_{{date}}.csv")),
            inc_ddm_lat_lon=True,
        )
        self.waypoints.dump_csv(
            path=path.joinpath(file_name_with_date("00_WAYPOINTS_DD_{{date}}.csv")),
            inc_dd_lat_lon=True,
        )

    def dump_gpx(self, path: Optional[Path] = None) -> None:
        """
        Write routes and waypoints as GPX files for use in GPS devices.

        This method builds a network wide GPX file using the `dumps_gpx()` methods for routes and waypoints.

        Files and directories currently use BAS Air Unit specific naming conventions - this will be addressed in #46.

        A GPX file containing all waypoints and a GPX for each route would normally be generated, but as they are not
        needed by BAS Air Unit they are currently disabled - this will be addressed in #46.

        :type path: Path
        :param path: base path for exported files
        """
        path = self._get_output_path(path=path, fmt_dir="GPX")

        gpx = GPX()
        gpx.waypoints = self.waypoints.dumps_gpx().waypoints
        gpx.routes = self.routes.dumps_gpx().routes
        with path.joinpath(file_name_with_date("00_NETWORK_{{date}}.gpx")).open(mode="w") as gpx_file:
            gpx_file.write(gpx.to_xml())

    def dump_fpl(self, path: Optional[Path] = None) -> None:
        """
        Write routes and waypoints as Garmin FPL files for use in aircraft GPS devices.

        This method is a wrapper around the `dump_fpl()` methods for routes and waypoints.

        Files and directories currently use BAS Air Unit specific naming conventions - this will be addressed in #46.

        :type path: Path
        :param path: base path for exported files
        """
        path = self._get_output_path(path=path, fmt_dir="FPL")

        self.waypoints.dump_fpl(path=path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}.fpl")))
        self.routes.dump_fpl(path=path, separate_files=True)

    def __repr__(self) -> str:
        """Represent NetworkManager as a string."""
        return f"<NetworkManager : {len(self.waypoints)} Waypoints - {len(self.routes)} Routes>"
