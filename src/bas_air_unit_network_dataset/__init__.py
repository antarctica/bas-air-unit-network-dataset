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
    identifier_max_length = 6
    name_max_length = 17

    feature_schema_spatial = {
        "geometry": "Point",
        "properties": {
            "id": "str",
            "identifier": "str",
            "name": "str",
            "colocated_with": "str",
            "last_accessed_at": "date",
            "last_accessed_by": "str",
            "comment": "str",
        },
    }

    csv_schema = {
        "identifier": "str",
        "name": "str",
        "colocated_with": "str",
        "last_accessed_at": "date",
        "last_accessed_by": "str",
        "comment": "str",
    }

    def __init__(
        self,
        identifier: Optional[str] = None,
        lon: Optional[float] = None,
        lat: Optional[float] = None,
        alt: Optional[float] = None,
        name: Optional[str] = None,
        colocated_with: Optional[str] = None,
        last_accessed_at: Optional[date] = None,
        last_accessed_by: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        self._id: str = str(ulid.new())

        self._identifier: str
        self._geometry: Point
        self._name: Optional[str] = None
        self._colocated_with: Optional[str] = None
        self._last_accessed_at: Optional[date] = None
        self._last_accessed_by: Optional[str] = None
        self._comment: Optional[str] = None

        if identifier is not None:
            self.identifier = identifier

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

        if name is not None:
            self.name = name

        if colocated_with is not None:
            self.colocated_with = colocated_with

        if last_accessed_at is not None and last_accessed_by is None:
            raise ValueError("A `last_accessed_by` value must be provided if `last_accessed_at` is set.")
        elif last_accessed_at is None and last_accessed_by is not None:
            raise ValueError("A `last_accessed_at` value must be provided if `last_accessed_by` is set.")
        elif last_accessed_at is not None and last_accessed_by is not None:
            self.last_accessed_at = last_accessed_at
            self.last_accessed_by = last_accessed_by

        if comment is not None:
            self.comment = comment

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, _id):
        self._id = str(ulid.from_str(_id))

    @property
    def identifier(self) -> str:
        return self._identifier

    @identifier.setter
    def identifier(self, identifier: str):
        if len(identifier) > Waypoint.identifier_max_length:
            raise ValueError(f"Identifiers must be 6 characters or less. '{identifier}' is {len(identifier)}.")

        self._identifier = identifier

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
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, name: str):
        if len(name) > Waypoint.name_max_length:
            raise ValueError(f"Names must be 17 characters or less. '{name}' is {len(name)}.")

        self._name = name

    @property
    def colocated_with(self) -> Optional[str]:
        return self._colocated_with

    @colocated_with.setter
    def colocated_with(self, colocated_with: str):
        self._colocated_with = colocated_with

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

    @property
    def comment(self) -> Optional[str]:
        return self._comment

    @comment.setter
    def comment(self, comment: str):
        self._comment = comment

    def loads_feature(self, feature: dict):
        self.id = feature["properties"]["id"]
        self.identifier = feature["properties"]["identifier"]
        self.geometry = list(feature["geometry"]["coordinates"])

        if feature["properties"]["name"] is not None:
            self.name = feature["properties"]["name"]

        if feature["properties"]["colocated_with"] is not None:
            self.colocated_with = feature["properties"]["colocated_with"]

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

        if feature["properties"]["comment"] is not None:
            self.comment = feature["properties"]["comment"]

    def dumps_feature_geometry(self) -> dict:
        geometry = {"type": "Point", "coordinates": (self.geometry.x, self.geometry.y)}
        if self.geometry.has_z:
            geometry["coordinates"] = (self.geometry.x, self.geometry.y, self.geometry.z)

        return geometry

    def dumps_feature(self, inc_spatial: bool = True) -> dict:
        feature = {
            "geometry": None,
            "properties": {
                "id": self.id,
                "identifier": self.identifier,
                "name": self.name,
                "colocated_with": self.colocated_with,
                "last_accessed_at": self.last_accessed_at,
                "last_accessed_by": self.last_accessed_by,
                "comment": self.comment,
            },
        }

        if inc_spatial:
            feature["geometry"] = self.dumps_feature_geometry()

        return feature

    def dumps_csv(self, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> dict:
        geometry_ddm = convert_coordinate_dd_2_ddm(lon=self.geometry.x, lat=self.geometry.y)

        name = "-"
        if self.name is not None:
            name = self.name

        colocated_with = "-"
        if self.colocated_with is not None:
            colocated_with = self.colocated_with

        last_accessed_at = "-"
        if self.last_accessed_at is not None:
            last_accessed_at = self.last_accessed_at.isoformat()

        last_accessed_by = "-"
        if self.last_accessed_by is not None:
            last_accessed_by = self.last_accessed_by

        comment = "-"
        if self.comment is not None:
            comment = self.comment

        csv_feature = {
            "identifier": self.identifier,
            "name": name,
            "colocated_with": colocated_with,
            "latitude_dd": self.geometry.y,
            "longitude_dd": self.geometry.x,
            "latitude_ddm": geometry_ddm["lat"],
            "longitude_ddm": geometry_ddm["lon"],
            "last_accessed_at": last_accessed_at,
            "last_accessed_by": last_accessed_by,
            "comment": comment,
        }

        if not inc_dd_lat_lon:
            del csv_feature["latitude_dd"]
            del csv_feature["longitude_dd"]
        if not inc_ddm_lat_lon:
            del csv_feature["latitude_ddm"]
            del csv_feature["longitude_ddm"]

        return csv_feature

    def dumps_gpx(self) -> GPXWaypoint:
        waypoint = GPXWaypoint()
        waypoint.name = self.identifier
        waypoint.longitude = self.geometry.x
        waypoint.latitude = self.geometry.y

        description_parts: List[str] = []
        if self.name is not None:
            description_parts.append(f"Name: {self.name}")
        if self.colocated_with is not None:
            description_parts.append(f"Co-Located with: {self.colocated_with}")
        if self.last_accessed_at is not None and self.last_accessed_by is not None:
            description_parts.append(f"Last assessed: {self.last_accessed_at.isoformat()}, by: {self.last_accessed_by}")
        if self.comment is not None:
            description_parts.append(f"Comment: {self.comment}")

        waypoint.description = "-"
        if len(description_parts) > 0:
            waypoint.description = " | ".join(description_parts)

        return waypoint

    def dumps_fpl(self) -> FplWaypoint:
        waypoint = FplWaypoint()

        waypoint.identifier = self.identifier
        waypoint.type = "USER WAYPOINT"
        waypoint.country_code = "__"
        waypoint.longitude = self.geometry.x
        waypoint.latitude = self.geometry.y

        if self.name is not None:
            waypoint.comment = self.name

        return waypoint

    def __repr__(self) -> str:
        return f"<Waypoint {self.id} :- [{self.identifier.ljust(6, '_')}], {self.geometry}>"


class RouteWaypoint:
    feature_schema = {
        "geometry": "None",
        "properties": {"route_id": "str", "waypoint_id": "str", "sequence": "int", "comment": "str"},
    }

    feature_schema_spatial = {
        "geometry": "Point",
        "properties": feature_schema["properties"],
    }

    def __init__(
        self, waypoint: Optional[Waypoint] = None, sequence: Optional[int] = None, comment: Optional[str] = None
    ) -> None:
        self._waypoint: Waypoint
        self._sequence: int
        self._comment: Optional[str] = None

        if waypoint is not None and sequence is None:
            raise ValueError("A `sequence` value must be provided if `waypoint` is set.")
        elif waypoint is None and sequence is not None:
            raise ValueError("A `waypoint` value must be provided if `sequence` is set.")
        elif waypoint is not None and sequence is not None:
            self.waypoint = waypoint
            self.sequence = sequence

        if comment is not None:
            self.comment = comment

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
    def comment(self) -> Optional[str]:
        # As BaseCamp has no support for route based waypoint comments, always return just the waypoint comment
        return self.waypoint.comment

    @comment.setter
    def comment(self, comment: str):
        self._comment = comment

    def loads_feature(self, feature: dict, waypoints: "WaypointCollection"):
        self.sequence = feature["properties"]["sequence"]
        self.comment = feature["properties"]["comment"]

        try:
            self.waypoint = waypoints[feature["properties"]["waypoint_id"]]
        except KeyError:
            raise KeyError(
                f"Waypoint with ID '{feature['properties']['waypoint_id']}' not found in available waypoints."
            )

    def dumps_feature(
        self,
        inc_spatial: bool = True,
        route_id: Optional[str] = None,
        route_name: Optional[str] = None,
        use_identifiers: bool = False,
    ) -> dict:
        feature = {
            "geometry": None,
            "properties": {
                "waypoint_id": self.waypoint.id,
                "sequence": self.sequence,
                "comment": self.comment,
            },
        }

        if inc_spatial:
            geometry = {"type": "Point", "coordinates": (self.waypoint.geometry.x, self.waypoint.geometry.y)}
            if self.waypoint.geometry.has_z:
                geometry["coordinates"] = (
                    self.waypoint.geometry.x,
                    self.waypoint.geometry.y,
                    self.waypoint.geometry.z,
                )
            feature["geometry"] = geometry

        if use_identifiers:
            del feature["properties"]["waypoint_id"]
            feature["properties"] = {**{"identifier": self.waypoint.identifier}, **feature["properties"]}

        if route_name is not None:
            feature["properties"] = {**{"route_name": route_name}, **feature["properties"]}

        if route_id is not None:
            feature["properties"] = {**{"route_id": route_id}, **feature["properties"]}

        return feature

    def dumps_csv(self, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False):
        route_waypoint = {"sequence": self.sequence}

        waypoint = self.waypoint.dumps_csv(inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon)
        del waypoint["comment"]
        del waypoint["last_accessed_at"]
        del waypoint["last_accessed_by"]

        route_waypoint = {**route_waypoint, **waypoint}

        comment = "-"
        if self.comment is not None:
            comment = self.comment
        route_waypoint["comment"] = comment

        return route_waypoint

    def dumps_gpx(self) -> GPXRoutePoint:
        route_waypoint = GPXRoutePoint()
        route_waypoint.name = self.waypoint.identifier
        route_waypoint.longitude = self.waypoint.geometry.x
        route_waypoint.latitude = self.waypoint.geometry.y
        route_waypoint.comment = self.comment

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
    feature_schema_waypoints_spatial["properties"]["identifier"] = "str"
    feature_schema_waypoints_spatial["properties"]["comment"] = "str"

    csv_schema_waypoints = {
        "sequence": "str",
        "identifier": "str",
        "name": "str",
        "colocated_with": "str",
        "comment": "str",
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

    def _dumps_feature_route(self, inc_spatial: bool = True) -> dict:
        feature = {
            "geometry": None,
            "properties": {"id": self.id, "name": self.name},
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
    ) -> List[dict]:
        _route_id = None
        if inc_route_id:
            _route_id = self.id

        _route_name = None
        if inc_route_name:
            _route_name = self.name

        features = []
        for route_waypoint in self.waypoints:
            features.append(
                route_waypoint.dumps_feature(
                    inc_spatial=inc_spatial, route_id=_route_id, route_name=_route_name, use_identifiers=use_identifiers
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
    ) -> Union[dict, List[dict]]:
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
    ) -> List[dict]:
        if not inc_waypoints:
            raise RuntimeError("Routes without waypoints cannot be dumped to CSV, set `inc_waypoints` to True.")

        csv_rows: List[Dict] = []
        for route_waypoint in self.waypoints:
            route_waypoint_csv_row = route_waypoint.dumps_csv(
                inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon
            )

            if route_column:
                route_waypoint_csv_row = {**{"route_name": self.name}, **route_waypoint_csv_row}

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
        # this process is very inelegant and needs improving to remove duplication [#110]
        fieldnames: List[str] = list(Route.csv_schema_waypoints.keys())
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
            fieldnames = ["route_name"] + fieldnames

        # newline parameter needed to avoid extra blank lines in files on Windows [#63]
        with open(path, mode="w", newline="") as output_file:
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
        with open(path, mode="w") as gpx_file:
            gpx_file.write(self.dumps_gpx(inc_waypoints=inc_waypoints).to_xml())

    def dumps_fpl(self, flight_plan_index: int) -> Fpl:
        fpl = Fpl()
        route = FplRoute()

        route.name = self.name
        route.index = flight_plan_index

        for route_waypoint in self.waypoints:
            route_point = FplRoutePoint()
            route_point.waypoint_identifier = route_waypoint.waypoint.identifier
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
            start = self.first_waypoint.waypoint.identifier.ljust(6)
            end = self.last_waypoint.waypoint.identifier.ljust(6)
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
        self._waypoints = sorted(self.waypoints, key=lambda x: x.identifier)

    def lookup(self, identifier: str) -> Optional[Waypoint]:
        for waypoint in self._waypoints:
            if waypoint.identifier == identifier:
                return waypoint

        return None

    def dump_features(self, inc_spatial: bool = True) -> List[dict]:
        features = []

        for waypoint in self.waypoints:
            features.append(waypoint.dumps_feature(inc_spatial=inc_spatial))

        return features

    def dump_csv(self, path: Path, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> None:
        # this process is very inelegant and needs improving to remove duplication [#110]
        fieldnames: List[str] = list(Waypoint.csv_schema.keys())
        if inc_dd_lat_lon:
            fieldnames = [
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

        # newline parameter needed to avoid extra blank lines in files on Windows [#63]
        with open(path, mode="w", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()

            for waypoint in self.waypoints:
                writer.writerow(waypoint.dumps_csv(inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon))

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
        self,
        inc_spatial: bool = True,
        inc_waypoints: bool = False,
        inc_route_id: bool = False,
        inc_route_name: bool = False,
    ) -> List[dict]:
        features = []

        for route in self.routes:
            if not inc_waypoints:
                features.append(route.dumps_feature(inc_spatial=inc_spatial, inc_waypoints=False))
                continue
            features += route.dumps_feature(
                inc_spatial=inc_spatial, inc_waypoints=True, inc_route_id=inc_route_id, inc_route_name=inc_route_name
            )

        return features

    def _dump_csv_separate(self, path: Path, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> None:
        for route in self.routes:
            route.dump_csv(
                path=path.joinpath(f"{route.name.upper()}.csv"),
                inc_waypoints=True,
                route_column=False,
                inc_dd_lat_lon=inc_dd_lat_lon,
                inc_ddm_lat_lon=inc_ddm_lat_lon,
            )

    def _dump_csv_combined(self, path: Path, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> None:
        fieldnames: List[str] = ["route_name"] + list(Route.csv_schema_waypoints.keys())

        route_waypoints: List[dict] = []
        for route in self.routes:
            route_waypoints += route.dumps_csv(
                inc_waypoints=True, route_column=True, inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon
            )

        # newline parameter needed to avoid extra blank lines in files on Windows [#63]
        with open(path, mode="w", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(route_waypoints)

    def dump_csv(
        self, path: Path, separate_files: bool = False, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False
    ) -> None:
        if separate_files:
            self._dump_csv_separate(path=path, inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon)
        else:
            self._dump_csv_combined(path=path, inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon)

    def dumps_gpx(self, inc_waypoints: bool = False) -> GPX:
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
        for route in self.routes:
            route.dump_gpx(path=path.joinpath(f"{route.name.upper()}.gpx"), inc_waypoints=inc_waypoints)

    def _dump_gpx_combined(self, path: Path) -> None:
        with open(path, mode="w") as gpx_file:
            gpx_file.write(self.dumps_gpx().to_xml())

    def dump_gpx(self, path: Path, separate_files: bool = False, inc_waypoints: bool = False) -> None:
        if separate_files:
            self._dump_gpx_separate(path=path, inc_waypoints=inc_waypoints)
        else:
            # combined GPX can't include waypoints as there'll be repetitions
            self._dump_gpx_combined(path=path)

    def dump_fpl(self, path: Path, separate_files: bool = False) -> None:
        if not separate_files:
            raise RuntimeError("FPL does not support combined routes, `separate_files` must be set to True.")

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
            # GDAL/Fiona doesn't create missing parent directories
            dataset_path.parent.mkdir(parents=True, exist_ok=True)
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
            layer.writerecords(self.waypoints.dump_features(inc_spatial=True))

        # route_waypoints
        with fiona.open(
            path, mode="w", driver="GPKG", schema=RouteWaypoint.feature_schema, layer="route_waypoints"
        ) as layer:
            layer.writerecords(self.routes.dumps_features(inc_spatial=False, inc_waypoints=True, inc_route_id=True))

        # routes
        # (only name and any other top/route level information is stored here, waypoints are stored in `route_waypoints`)
        with fiona.open(
            path, mode="w", driver="GPKG", crs=crs_from_epsg(4326), schema=Route.feature_schema, layer="routes"
        ) as layer:
            layer.writerecords(self.routes.dumps_features(inc_spatial=False, inc_waypoints=False))

    def load_gpx(self, path: Path) -> None:
        with open(path, mode="r", encoding="utf-8-sig") as gpx_file:
            gpx_data = gpx_parse(gpx_file)

        # waypoints
        for waypoint in gpx_data.waypoints:
            _waypoint = Waypoint()
            _waypoint.identifier = waypoint.name
            _waypoint.geometry = [waypoint.longitude, waypoint.latitude]

            if waypoint.description is not None and waypoint.description != "N/A | N/A | N/A | N/A | N/A":
                comment_elements = waypoint.description.split(" | ")
                if comment_elements[0] != "N/A":
                    _waypoint.name = comment_elements[0]
                if comment_elements[1] != "N/A":
                    _waypoint.colocated_with = comment_elements[1]
                if comment_elements[2] != "N/A":
                    _waypoint.last_accessed_at = date.fromisoformat(comment_elements[2])
                if comment_elements[3] != "N/A":
                    _waypoint.last_accessed_by = comment_elements[3]
                if comment_elements[4] != "N/A":
                    _waypoint.comment = comment_elements[4]

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
                _comment = None

                _route_waypoint = RouteWaypoint(waypoint=_waypoint, sequence=sequence, comment=_comment)
                _route.waypoints.append(_route_waypoint)
                sequence += 1

            self.routes.append(_route)

        # once data is loaded, save to GeoPackage
        self._dump_gpkg(path=self.dataset_path)

    def dump_csv(self, path: Optional[Path] = None) -> None:
        path = self._get_output_path(path=path, fmt_dir="CSV")

        self.waypoints.dump_csv(
            path=path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}.csv")), inc_ddm_lat_lon=True
        )
        self.waypoints.dump_csv(
            path=path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}_DD.csv")), inc_dd_lat_lon=True
        )
        # combined/individual routes files omitted as they aren't needed by the Air Unit (#101)

    def dump_gpx(self, path: Optional[Path] = None) -> None:
        path = self._get_output_path(path=path, fmt_dir="GPX")

        # waypoints and combined/individual routes files omitted as they aren't needed by the Air Unit (#101)

        # `network.gpx` needs access to both routes and waypoints so needs to be done at this level
        gpx = GPX()
        gpx.waypoints = self.waypoints.dumps_gpx().waypoints
        gpx.routes = self.routes.dumps_gpx().routes
        with open(path.joinpath(file_name_with_date("00_NETWORK_{{date}}.gpx")), mode="w") as gpx_file:
            gpx_file.write(gpx.to_xml())

    def dump_fpl(self, path: Optional[Path] = None) -> None:
        path = self._get_output_path(path=path, fmt_dir="FPL")

        self.waypoints.dump_fpl(path=path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}.fpl")))
        self.routes.dump_fpl(path=path, separate_files=True)

    def __repr__(self):
        return f"<NetworkManager : {len(self.waypoints)} Waypoints - {len(self.routes)} Routes>"
