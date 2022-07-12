from collections import OrderedDict
import csv
from datetime import date
from pathlib import Path
from typing import Optional, List, Dict, Iterator, Union

import fiona
import ulid
from fiona.crs import from_epsg as crs_from_epsg
from gpxpy.gpx import GPX, GPXWaypoint, GPXRoute, GPXRoutePoint
from gpxpy import parse as gpx_parse
from shapely.geometry import Point

from bas_air_unit_network_dataset.exporters.fpl import (
    Fpl,
    Waypoint as FplWaypoint,
    Route as FplRoute,
    RoutePoint as FplRoutePoint,
)
from bas_air_unit_network_dataset.utils import convert_coordinate_dd_2_ddm, file_name_with_date


class Waypoint:
    designator_max_length = 6

    feature_schema_spatial = {
        "geometry": "Point",
        "properties": {
            "id": "str",
            "designator": "str",
            "comment": "str",
            "last_accessed_at": "date",
            "last_accessed_by": "str",
        },
    }

    csv_schema = {
        "designator": "str",
        "comment": "str",
        "longitude_dd": "float",
        "latitude_dd": "float",
        "longitude_ddm": "float",
        "latitude_ddm": "float",
        "last_accessed_at": "date",
        "last_accessed_by": "str",
    }

    def __init__(
        self,
        designator: Optional[str] = None,
        lon: Optional[float] = None,
        lat: Optional[float] = None,
        alt: Optional[float] = None,
        comment: Optional[str] = None,
        last_accessed_at: Optional[date] = None,
        last_accessed_by: Optional[str] = None,
    ) -> None:
        self._id: str = str(ulid.new())

        self._designator: str
        self._geometry: Point
        self._comment: Optional[str] = None
        self._last_accessed_at: Optional[date] = None
        self._last_accessed_by: Optional[str] = None

        if designator is not None:
            self.designator = designator

        _geometry = []
        if lat is None and lon is not None:
            raise ValueError("A latitude (`lat`) value must be provided if longitude (`lon`) is set.")
        if lat is not None and lon is None:
            raise ValueError("A longitude (`lon`) value must be provided if latitude (`lat`) is set.")
        elif lat is not None and lon is not None and alt is None:
            _geometry = [lon, lat]
        elif lat is not None and lon is not None and alt is not None:
            _geometry = [lon, lat, alt]
        if len(_geometry) >= 2:
            self.geometry = _geometry

        if comment is not None:
            self.comment = comment

        if last_accessed_at is not None and last_accessed_by is None:
            raise ValueError("A `last_accessed_by` value must be provided if `last_accessed_at` is set.")
        elif last_accessed_at is None and last_accessed_by is not None:
            raise ValueError("A `last_accessed_at` value must be provided if `last_accessed_by` is set.")
        elif last_accessed_at is not None and last_accessed_by is not None:
            self.last_accessed_at = last_accessed_at
            self.last_accessed_by = last_accessed_by

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, _id):
        self._id = str(ulid.from_str(_id))

    @property
    def designator(self) -> str:
        return self._designator

    @designator.setter
    def designator(self, designator: str):
        if len(designator) > Waypoint.designator_max_length:
            raise ValueError(f"Designators must be 6 characters or less. '{designator}' is {len(designator)}.")

        self._designator = designator

    @property
    def geometry(self) -> Point:
        return self._geometry

    @geometry.setter
    def geometry(self, geometry: List[float]):
        lon = geometry[0]
        if lon < -180 or lon > 180:
            raise ValueError(f"Invalid Longitude, must be -180<=X<=180 not {lon}.")
        lat = geometry[1]
        if lat < -90 or lat > 90:
            raise ValueError(f"Invalid Latitude, must be -90<=Y<=+90 not {lat}.")
        self._geometry = Point(lon, lat)

        try:
            alt = geometry[2]
            self._geometry = Point(lon, lat, alt)
        except IndexError:
            pass

    @property
    def comment(self) -> Optional[str]:
        return self._comment

    @comment.setter
    def comment(self, comment: str):
        self._comment = comment

    @property
    def last_accessed_at(self) -> Optional[date]:
        return self._last_accessed_at

    @last_accessed_at.setter
    def last_accessed_at(self, _date: date):
        self._last_accessed_at = _date

    @property
    def last_accessed_by(self) -> Optional[str]:
        return self._last_accessed_by

    @last_accessed_by.setter
    def last_accessed_by(self, last_accessed_by: str):
        self._last_accessed_by = last_accessed_by

    def loads_feature(self, feature: dict):
        self.id = feature["properties"]["id"]
        self.designator = feature["properties"]["designator"]
        self.geometry = list(feature["geometry"]["coordinates"])

        if feature["properties"]["comment"] is not None:
            self.comment = feature["properties"]["comment"]

        if feature["properties"]["last_accessed_at"] is not None and feature["properties"]["last_accessed_by"] is None:
            raise ValueError("A `last_accessed_by` value must be provided if `last_accessed_at` is set.")
        elif (
            feature["properties"]["last_accessed_at"] is None and feature["properties"]["last_accessed_by"] is not None
        ):
            raise ValueError("A `last_accessed_at` value must be provided if `last_accessed_by` is set.")
        elif (
            feature["properties"]["last_accessed_at"] is not None
            and feature["properties"]["last_accessed_by"] is not None
        ):
            self.last_accessed_at = date.fromisoformat(feature["properties"]["last_accessed_at"])
            self.last_accessed_by = feature["properties"]["last_accessed_by"]

    def dumps_feature_geometry(self) -> dict:
        geometry = {"type": "Point", "coordinates": (self.geometry.x, self.geometry.y)}
        if self.geometry.has_z:
            geometry["coordinates"] = (self.geometry.x, self.geometry.y, self.geometry.z)

        return geometry

    def dumps_feature(self, spatial: bool = True) -> dict:
        feature = {
            "geometry": None,
            "properties": {
                "id": self.id,
                "designator": self.designator,
                "comment": self.comment,
                "last_accessed_at": self.last_accessed_at,
                "last_accessed_by": self.last_accessed_by,
            },
        }

        if spatial:
            feature["geometry"] = self.dumps_feature_geometry()

        return feature

    def dumps_csv(self) -> dict:
        comment = "-"
        if self.comment is not None:
            comment = self.comment

        last_accessed_at = "-"
        if self.last_accessed_at is not None:
            last_accessed_at = self.last_accessed_at.isoformat()

        last_accessed_by = "-"
        if self.last_accessed_by is not None:
            last_accessed_by = self.last_accessed_by

        geometry_ddm = convert_coordinate_dd_2_ddm(lon=self.geometry.x, lat=self.geometry.y)

        return {
            "designator": self.designator,
            "latitude_dd": self.geometry.y,
            "longitude_dd": self.geometry.x,
            "latitude_ddm": geometry_ddm["lat"],
            "longitude_ddm": geometry_ddm["lon"],
            "comment": comment,
            "last_accessed_at": last_accessed_at,
            "last_accessed_by": last_accessed_by,
        }

    def dumps_gpx(self) -> GPXWaypoint:
        waypoint = GPXWaypoint()
        waypoint.name = self.designator
        waypoint.longitude = self.geometry.x
        waypoint.latitude = self.geometry.y

        waypoint.description = "[No Description] [Last Access Unknown]"

        _comment = None
        if self.comment is not None:
            _comment = self.comment

        _access = None
        if self.last_accessed_at is not None and self.last_accessed_by is None:
            _access = f"Last checked: {self.last_accessed_at.isoformat()}"
        elif self.last_accessed_at is not None and self.last_accessed_by is not None:
            _access = f"Last checked: {self.last_accessed_at.isoformat()}, by: {self.last_accessed_by}"

        if _comment is not None and _access is not None:
            waypoint.description = f"{_comment} - {_access}"
        elif _comment is not None and _access is None:
            waypoint.description = _comment
        elif _comment is None and _access is not None:
            waypoint.description = _access

        return waypoint

    def dumps_fpl(self) -> FplWaypoint:
        waypoint = FplWaypoint()

        waypoint.identifier = self.designator
        waypoint.type = "USER WAYPOINT"
        waypoint.country_code = "__"
        waypoint.longitude = self.geometry.x
        waypoint.latitude = self.geometry.y

        if self.comment is not None:
            # FPL comments can only be 25 characters long. This limitation isn't enforced in input data currently so
            # as a crude measure, the comment is truncated to the first 25 characters.
            waypoint.comment = self.comment[:25]

        return waypoint

    def __repr__(self) -> str:
        return f"<Waypoint {self.id} :- [{self.designator.ljust(6, '_')}], {self.geometry}>"


class RouteWaypoint:
    feature_schema = {
        "geometry": "None",
        "properties": {"route_id": "str", "waypoint_id": "str", "sequence": "int", "description": "str"},
    }

    feature_schema_spatial = {
        "geometry": "Point",
        "properties": feature_schema["properties"],
    }

    def __init__(
        self, waypoint: Optional[Waypoint] = None, sequence: Optional[int] = None, description: Optional[str] = None
    ) -> None:
        self._waypoint: Waypoint
        self._sequence: int
        self._description: Optional[str] = None

        if waypoint is not None and sequence is None:
            raise ValueError("A `sequence` value must be provided if `waypoint` is set.")
        elif waypoint is None and sequence is not None:
            raise ValueError("A `waypoint` value must be provided if `sequence` is set.")
        elif waypoint is not None and sequence is not None:
            self.waypoint = waypoint
            self.sequence = sequence

        if description is not None:
            self.description = description

    @property
    def waypoint(self) -> Waypoint:
        return self._waypoint

    @waypoint.setter
    def waypoint(self, waypoint: Waypoint):
        self._waypoint = waypoint

    @property
    def sequence(self) -> int:
        return self._sequence

    @sequence.setter
    def sequence(self, sequence: int):
        self._sequence = sequence

    @property
    def description(self) -> Optional[str]:
        # As BaseCamp has no support for route based waypoint comments, always return just the waypoint comment
        return self.waypoint.comment

        # if self._description is None and self.waypoint.comment is None:
        #     return "[No Description]"
        # if self._description is None and self.waypoint.comment is not None:
        #     return self.waypoint.comment
        # if self._description is not None and self.waypoint.comment is not None:
        #     return f"{self._description} - {self.waypoint.comment}"
        #
        # return self._description

    @description.setter
    def description(self, description: str):
        self._description = description

    def loads_feature(self, feature: dict, waypoints: "WaypointCollection"):
        self.sequence = feature["properties"]["sequence"]
        self.description = feature["properties"]["description"]

        try:
            self.waypoint = waypoints[feature["properties"]["waypoint_id"]]
        except KeyError:
            raise KeyError(
                f"Waypoint with ID '{feature['properties']['waypoint_id']}' not found in available waypoints."
            )

    def dumps_feature(
        self,
        spatial: bool = True,
        route_id: Optional[str] = None,
        route_name: Optional[str] = None,
        use_designators: bool = False,
    ) -> dict:
        feature = {
            "geometry": None,
            "properties": {
                "waypoint_id": self.waypoint.id,
                "sequence": self.sequence,
                "description": self.description,
            },
        }

        if spatial:
            geometry = {"type": "Point", "coordinates": (self.waypoint.geometry.x, self.waypoint.geometry.y)}
            if self.waypoint.geometry.has_z:
                geometry["coordinates"] = (
                    self.waypoint.geometry.x,
                    self.waypoint.geometry.y,
                    self.waypoint.geometry.z,
                )
            feature["geometry"] = geometry

        if use_designators:
            del feature["properties"]["waypoint_id"]
            feature["properties"] = {**{"designator": self.waypoint.designator}, **feature["properties"]}

        if route_name is not None:
            feature["properties"] = {**{"route_name": route_name}, **feature["properties"]}

        if route_id is not None:
            feature["properties"] = {**{"route_id": route_id}, **feature["properties"]}

        return feature

    def dumps_csv(self):
        route_waypoint = {"sequence": self.sequence}

        waypoint = self.waypoint.dumps_csv()
        del waypoint["comment"]
        del waypoint["last_accessed_at"]
        del waypoint["last_accessed_by"]

        route_waypoint = {**route_waypoint, **waypoint}
        route_waypoint["description"] = self.description

        return route_waypoint

    def dumps_gpx(self) -> GPXRoutePoint:
        route_waypoint = GPXRoutePoint()
        route_waypoint.name = self.waypoint.designator
        route_waypoint.longitude = self.waypoint.geometry.x
        route_waypoint.latitude = self.waypoint.geometry.y
        route_waypoint.description = self.description

        return route_waypoint


class Route:
    feature_schema = {
        "geometry": "None",
        "properties": {"id": "str", "name": "str"},
    }

    feature_schema_spatial = {
        "geometry": "LineString",
        "properties": {"id": "str", "name": "str"},
    }

    # TODO: Determine why this requires an ordered dict when other schemas don't
    feature_schema_waypoints_spatial = {"geometry": "Point", "properties": OrderedDict()}
    feature_schema_waypoints_spatial["properties"]["sequence"] = "int"
    feature_schema_waypoints_spatial["properties"]["designator"] = "str"
    feature_schema_waypoints_spatial["properties"]["description"] = "str"

    csv_schema_waypoints = {
        "sequence": "str",
        "designator": "str",
        "longitude_dd": "float",
        "latitude_dd": "float",
        "longitude_ddm": "float",
        "latitude_ddm": "float",
        "description": "str",
    }

    def __init__(
        self,
        name: Optional[str] = None,
        route_waypoints: Optional[List[Dict[str, Union[str, Waypoint]]]] = None,
    ) -> None:
        self._id: str = str(ulid.new())

        self._name: str
        self._waypoints: List[RouteWaypoint] = []

        if name is not None:
            self.name = name

        if route_waypoints is not None:
            self.waypoints = route_waypoints

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, _id: str):
        self._id = str(ulid.from_str(_id))

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def waypoints(self) -> List[RouteWaypoint]:
        return self._waypoints

    @waypoints.setter
    def waypoints(self, route_waypoints: List[RouteWaypoint]):
        self._waypoints = route_waypoints

    @property
    def first_waypoint(self) -> Optional[RouteWaypoint]:
        try:
            return self.waypoints[0]
        except IndexError:
            return None

    @property
    def last_waypoint(self) -> Optional[RouteWaypoint]:
        try:
            return self.waypoints[-1]
        except IndexError:
            return None

    @property
    def waypoints_count(self) -> int:
        return len(self.waypoints)

    def loads_feature(self, feature: dict):
        self.id = feature["properties"]["id"]
        self.name = feature["properties"]["name"]

    def _dumps_feature_route(self, spatial: bool = True) -> dict:
        feature = {
            "geometry": None,
            "properties": {"id": self.id, "name": self.name},
        }

        if spatial:
            geometry = []
            for route_waypoint in self.waypoints:
                geometry.append(route_waypoint.waypoint.dumps_feature_geometry()["coordinates"])
            feature["geometry"] = {"type": "LineString", "coordinates": geometry}

        return feature

    def _dumps_feature_waypoints(
        self, spatial: bool = True, route_id: bool = False, route_name: bool = False, use_designators: bool = False
    ) -> List[dict]:
        _route_id = None
        if route_id:
            _route_id = self.id

        _route_name = None
        if route_name:
            _route_name = self.name

        features = []
        for route_waypoint in self.waypoints:
            features.append(
                route_waypoint.dumps_feature(
                    spatial=spatial, route_id=_route_id, route_name=_route_name, use_designators=use_designators
                )
            )

        return features

    def dumps_feature(
        self,
        spatial: bool = True,
        waypoints: bool = False,
        route_id: bool = False,
        route_name: bool = False,
        use_designators: bool = False,
    ) -> Union[dict, List[dict]]:
        if not waypoints:
            return self._dumps_feature_route(spatial=spatial)

        return self._dumps_feature_waypoints(
            spatial=spatial, route_id=route_id, route_name=route_name, use_designators=use_designators
        )

    def dumps_csv(self, waypoints: bool = False, route_column: bool = False) -> List[dict]:
        if not waypoints:
            raise RuntimeError("Routes without waypoints cannot be dumped to CSV, set `waypoints` to True.")

        csv_rows: List[Dict] = []
        for route_waypoint in self.waypoints:
            route_waypoint_csv_row = route_waypoint.dumps_csv()

            if route_column:
                route_waypoint_csv_row = {**{"route_name": self.name}, **route_waypoint_csv_row}

            csv_rows.append(route_waypoint_csv_row)

        return csv_rows

    def dump_csv(self, path: Path, waypoints: bool = False, route_column: bool = False) -> None:
        fieldnames: List[str] = list(Route.csv_schema_waypoints.keys())
        if route_column:
            fieldnames = ["route_name"] + fieldnames

        # newline parameter needed to avoid extra blank lines in files on Windows [#63]
        with open(path, mode="w", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.dumps_csv(waypoints=waypoints, route_column=route_column))

    def dumps_gpx(self, waypoints: bool = False) -> GPX:
        gpx = GPX()
        route = GPXRoute()

        route.name = self.name

        for route_waypoint in self.waypoints:
            route.points.append(route_waypoint.dumps_gpx())

            if waypoints:
                gpx.waypoints.append(route_waypoint.waypoint.dumps_gpx())

        gpx.routes.append(route)

        return gpx

    def dump_gpx(self, path: Path, waypoints: bool = False) -> None:
        with open(path, mode="w") as gpx_file:
            gpx_file.write(self.dumps_gpx(waypoints=waypoints).to_xml())

    def dumps_fpl(self, flight_plan_index: int) -> Fpl:
        fpl = Fpl()
        route = FplRoute()

        route.name = self.name
        route.index = flight_plan_index

        for route_waypoint in self.waypoints:
            route_point = FplRoutePoint()
            route_point.waypoint_identifier = route_waypoint.waypoint.designator
            route_point.waypoint_type = "USER WAYPOINT"
            route_point.waypoint_country_code = "__"
            route.points.append(route_point)

        fpl.route = route
        fpl.validate()

        return fpl

    def dump_fpl(self, path: Path, flight_plan_index: int) -> None:
        with open(path, mode="w") as xml_file:
            xml_file.write(self.dumps_fpl(flight_plan_index=flight_plan_index).dumps_xml().decode())

    def __repr__(self) -> str:
        start = "-"
        end = "-"

        try:
            start = self.first_waypoint.waypoint.designator.ljust(6)
            end = self.last_waypoint.waypoint.designator.ljust(6)
        except AttributeError:
            pass

        return f"<Route {self.id} :- [{self.name.ljust(10, '_')}], {self.waypoints_count} waypoints, Start/End: {start} / {end}>"


class WaypointCollection:
    def __init__(self) -> None:
        self._waypoints: List[Waypoint] = []

    @property
    def waypoints(self) -> List[Waypoint]:
        return self._waypoints

    def append(self, waypoint: Waypoint) -> None:
        self._waypoints.append(waypoint)

    def lookup(self, designator: str) -> Optional[Waypoint]:
        for waypoint in self._waypoints:
            if waypoint.designator == designator:
                return waypoint

        return None

    def dump_features(self, spatial: bool = True) -> List[dict]:
        features = []

        for waypoint in self.waypoints:
            features.append(waypoint.dumps_feature(spatial=spatial))

        return features

    def dump_csv(self, path: Path) -> None:
        # newline parameter needed to avoid extra blank lines in files on Windows [#63]
        with open(path, mode="w", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=list(Waypoint.csv_schema.keys()))
            writer.writeheader()

            for waypoint in self.waypoints:
                writer.writerow(waypoint.dumps_csv())

    def dumps_gpx(self) -> GPX:
        gpx = GPX()

        for waypoint in self.waypoints:
            gpx.waypoints.append(waypoint.dumps_gpx())

        return gpx

    def dump_gpx(self, path: Path) -> None:
        with open(path, mode="w") as gpx_file:
            gpx_file.write(self.dumps_gpx().to_xml())

    def dumps_fpl(self) -> Fpl:
        fpl = Fpl()

        for waypoint in self.waypoints:
            fpl.waypoints.append(waypoint.dumps_fpl())

        fpl.validate()

        return fpl

    def dump_fpl(self, path: Path) -> None:
        fpl = self.dumps_fpl()
        fpl.dump_xml(path=path)

    def __getitem__(self, _id: str) -> Waypoint:
        for waypoint in self._waypoints:
            if waypoint.id == _id:
                return waypoint

        raise KeyError(_id)

    def __iter__(self) -> Iterator[Waypoint]:
        return self._waypoints.__iter__()

    def __len__(self):
        return len(self.waypoints)

    def __repr__(self) -> str:
        return f"<WaypointCollection : {self.__len__()} waypoints>"


class RouteCollection:
    def __init__(self) -> None:
        self._routes: List[Route] = []

    @property
    def routes(self) -> List[Route]:
        return self._routes

    def append(self, route: Route) -> None:
        self._routes.append(route)

    def dumps_features(
        self, spatial: bool = True, waypoints: bool = False, route_id: bool = False, route_name: bool = False
    ) -> List[dict]:
        features = []

        for route in self.routes:
            if not waypoints:
                features.append(route.dumps_feature(spatial=spatial, waypoints=False))
                continue
            features += route.dumps_feature(spatial=spatial, waypoints=True, route_id=route_id, route_name=route_name)

        return features

    def _dump_csv_separate(self, path: Path) -> None:
        for route in self.routes:
            route.dump_csv(path=path.joinpath(f"{route.name.upper()}.csv"), waypoints=True, route_column=False)

    def _dump_csv_combined(self, path: Path) -> None:
        fieldnames: List[str] = ["route_name"] + list(Route.csv_schema_waypoints.keys())

        route_waypoints: List[dict] = []
        for route in self.routes:
            route_waypoints += route.dumps_csv(waypoints=True, route_column=True)

        # newline parameter needed to avoid extra blank lines in files on Windows [#63]
        with open(path, mode="w", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(route_waypoints)

    def dump_csv(self, path: Path, separate: bool = False) -> None:
        if separate:
            self._dump_csv_separate(path=path)
        else:
            self._dump_csv_combined(path=path)

    def dumps_gpx(self, waypoints: bool = False) -> GPX:
        gpx = GPX()
        _waypoints = []

        for route in self.routes:
            gpx.routes.append(route.dumps_gpx(waypoints=False).routes[0])

            if waypoints:
                _waypoints += route.dumps_gpx(waypoints=True).waypoints

        if waypoints:
            gpx.waypoints = _waypoints

        return gpx

    def _dump_gpx_separate(self, path: Path, waypoints: bool = False) -> None:
        for route in self.routes:
            route.dump_gpx(path=path.joinpath(f"{route.name.upper()}.gpx"), waypoints=waypoints)

    def _dump_gpx_combined(self, path: Path) -> None:
        with open(path, mode="w") as gpx_file:
            gpx_file.write(self.dumps_gpx().to_xml())

    def dump_gpx(self, path: Path, separate: bool = False, waypoints: bool = False) -> None:
        if separate:
            self._dump_gpx_separate(path=path, waypoints=waypoints)
        else:
            # combined GPX can't include waypoints as there'll be repetitions
            self._dump_gpx_combined(path=path)

    def dump_fpl(self, path: Path, separate: bool = False) -> None:
        if not separate:
            raise RuntimeError("FPL does not support combined routes, `separate` must be set to True.")

        flight_plan_index = 1
        for route in self.routes:
            route.dump_fpl(path=path.joinpath(f"{route.name.upper()}.fpl"), flight_plan_index=flight_plan_index)
            flight_plan_index += 1

    def __getitem__(self, _id: str) -> Route:
        for route in self.routes:
            if route.id == _id:
                return route

        raise KeyError(_id)

    def __iter__(self) -> Iterator[Route]:
        return self.routes.__iter__()

    def __len__(self):
        return len(self.routes)

    def __repr__(self) -> str:
        return f"<RouteCollection : {self.__len__()} routes>"


class NetworkManager:
    # If you can come up with a better name for this class, you could win a prize!

    def __init__(self, dataset_path: Path, output_path: Optional[Path] = None, init: Optional[bool] = False):
        self.waypoints: WaypointCollection = WaypointCollection()
        self.routes: RouteCollection = RouteCollection()

        if init:
            self._dump_gpkg(path=dataset_path)

        self.dataset_path = dataset_path
        self._load_gpkg(path=self.dataset_path)

        self.output_path: Optional[Path] = None
        if output_path is not None:
            if not dataset_path.exists():
                raise FileNotFoundError("Output path does not exist.")
            self.output_path = output_path

    def _get_output_path(self, path: Optional[Path], fmt_dir: Optional[str] = None) -> Path:
        if path is None and self.output_path is not None:
            path = self.output_path

        if path is None:
            raise FileNotFoundError("No output path specified")

        path = path.resolve()
        if fmt_dir is not None:
            path = path.joinpath(fmt_dir)

        path.mkdir(parents=True, exist_ok=True)

        if not path.exists():
            raise FileNotFoundError("Output path does not exist.")

        return path

    def _load_gpkg(self, path: Optional[Path] = None) -> None:
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
            route_waypoints_by_route_id: Dict[str, List[RouteWaypoint]] = {}
            for route_waypoint_feature in layer:
                route_waypoint = RouteWaypoint()
                route_waypoint.loads_feature(feature=route_waypoint_feature, waypoints=self.waypoints)

                if route_waypoint_feature["properties"]["route_id"] not in route_waypoints_by_route_id.keys():
                    route_waypoints_by_route_id[route_waypoint_feature["properties"]["route_id"]] = []
                route_waypoints_by_route_id[route_waypoint_feature["properties"]["route_id"]].append(route_waypoint)

            for route_id, route_waypoint_features in route_waypoints_by_route_id.items():
                route = self.routes[route_id]
                route.waypoints = route_waypoint_features

    def _dump_gpkg(self, path: Path) -> None:
        # waypoints
        with fiona.open(
            path,
            mode="w",
            driver="GPKG",
            crs=crs_from_epsg(4326),
            schema=Waypoint.feature_schema_spatial,
            layer="waypoints",
        ) as layer:
            layer.writerecords(self.waypoints.dump_features(spatial=True))

        # route_waypoints
        with fiona.open(
            path, mode="w", driver="GPKG", schema=RouteWaypoint.feature_schema, layer="route_waypoints"
        ) as layer:
            layer.writerecords(self.routes.dumps_features(spatial=False, waypoints=True, route_id=True))

        # routes
        # (only name and any other top/route level information is stored here, waypoints are stored in `route_waypoints`)
        with fiona.open(
            path, mode="w", driver="GPKG", crs=crs_from_epsg(4326), schema=Route.feature_schema, layer="routes"
        ) as layer:
            layer.writerecords(self.routes.dumps_features(spatial=False, waypoints=False))

    def load_gpx(self, path: Path) -> None:
        with open(path, mode="r") as gpx_file:
            gpx_data = gpx_parse(gpx_file)

        # waypoints
        for waypoint in gpx_data.waypoints:
            _waypoint = Waypoint()
            _waypoint.designator = waypoint.name
            _waypoint.geometry = [waypoint.longitude, waypoint.latitude]

            if waypoint.description is not None and waypoint.description != "N/A | N/A | N/A | N/A":
                comment_elements = waypoint.description.split(" | ")
                _waypoint.comment = f"{comment_elements[0]} | {comment_elements[3]}"
                if comment_elements[1] != "N/A":
                    _waypoint.last_accessed_at = date.fromisoformat(comment_elements[1])
                if comment_elements[2] != "N/A":
                    _waypoint.last_accessed_by = comment_elements[2]

            self.waypoints.append(_waypoint)

        # routes & route-waypoints
        for route in gpx_data.routes:
            _route = Route()
            _route.name = route.name

            sequence = 1
            for route_waypoint in route.points:
                _waypoint = self.waypoints.lookup(route_waypoint.name)

                # ignore route waypoint descriptions, as BaseCamp just copies the waypoint description, rather than
                # having a contextual description for each waypoint within a route.
                _description = None

                _route_waypoint = RouteWaypoint(waypoint=_waypoint, sequence=sequence, description=_description)
                _route.waypoints.append(_route_waypoint)
                sequence += 1

            self.routes.append(_route)

        # once data is loaded, save to GeoPackage
        self._dump_gpkg(path=self.dataset_path)

    def dump_csv(self, path: Optional[Path] = None) -> None:
        path = self._get_output_path(path=path, fmt_dir="CSV")

        self.waypoints.dump_csv(path=path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}.csv")))
        self.routes.dump_csv(path=path.joinpath(file_name_with_date("00_ROUTES_{{date}}.csv")))
        self.routes.dump_csv(path=path, separate=True)

    def dump_gpx(self, path: Optional[Path] = None) -> None:
        path = self._get_output_path(path=path, fmt_dir="GPX")

        self.waypoints.dump_gpx(path=path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}.gpx")))
        self.routes.dump_gpx(path=path.joinpath(file_name_with_date("00_ROUTES_{{date}}.gpx")), waypoints=False)
        self.routes.dump_gpx(path=path, separate=True, waypoints=False)

        # `network.gpx` needs access to both routes and waypoints so needs to be done at this level
        gpx = GPX()
        gpx.waypoints = self.waypoints.dumps_gpx().waypoints
        gpx.routes = self.routes.dumps_gpx().routes
        with open(path.joinpath(file_name_with_date("00_NETWORK_{{date}}.gpx")), mode="w") as gpx_file:
            gpx_file.write(gpx.to_xml())

    def dump_fpl(self, path: Optional[Path] = None) -> None:
        path = self._get_output_path(path=path, fmt_dir="FPL")

        self.waypoints.dump_fpl(path=path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}.fpl")))
        self.routes.dump_fpl(path=path, separate=True)

    def __repr__(self):
        return f"<NetworkManager : {len(self.waypoints)} Waypoints - {len(self.routes)} Routes>"
