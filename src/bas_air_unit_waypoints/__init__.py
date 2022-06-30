import csv
from datetime import date
from pathlib import Path
from typing import Optional, List, Dict, Iterator, Union

import fiona
import ulid
from fiona.crs import from_epsg as crs_from_epsg
from shapely.geometry import Point


class Waypoint:
    designator_max_length = 6

    feature_schema = {
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
        "longitude": "float",
        "latitude": "float",
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

    def dumps_feature(self) -> dict:
        _geometry = {"type": "Point", "coordinates": (self.geometry.x, self.geometry.y)}
        if self.geometry.has_z:
            _geometry["coordinates"] = (self.geometry.x, self.geometry.y, self.geometry.z)

        return {
            "geometry": _geometry,
            "properties": {
                "id": self.id,
                "designator": self.designator,
                "comment": self.comment,
                "last_accessed_at": self.last_accessed_at,
                "last_accessed_by": self.last_accessed_by,
            },
        }

    def __repr__(self) -> str:
        return f"<Waypoint {self.id} :- [{self.designator.ljust(6, '_')}], {self.geometry}>"


class RouteWaypoint:
    feature_schema = {
        "geometry": "None",
        "properties": {"route_id": "str", "waypoint_id": "str", "description": "str", "sequence": "int"},
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
    def description(self) -> str:
        return self._description

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

    def dumps_feature(self, route_id: str) -> dict:
        return {
            "properties": {
                "route_id": route_id,
                "sequence": self.sequence,
                "waypoint_id": self.waypoint.id,
                "description": self.description,
            }
        }


class Route:
    feature_schema = {
        "geometry": "None",
        "properties": {"id": "str", "name": "str"},
    }

    csv_schema = {"sequence": "str", "designator": "str", "longitude": "float", "latitude": "float", "description": str}

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

    def dumps_feature(self) -> dict:
        return {
            "properties": {"id": self.id, "name": self.name},
        }

    def dumps_csv(self) -> List[dict]:
        csv_rows: List[Dict] = []

        for route_waypoint in self.waypoints:
            csv_rows.append(
                {
                    "sequence": route_waypoint.sequence,
                    "designator": route_waypoint.waypoint.designator,
                    "latitude": route_waypoint.waypoint.geometry.y,
                    "longitude": route_waypoint.waypoint.geometry.x,
                    "description": route_waypoint.description,
                }
            )

        return csv_rows

    def dump_csv(self, path: Path) -> None:
        with open(path, mode="w") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=list(Route.csv_schema.keys()))
            writer.writeheader()
            writer.writerows(self.dumps_csv())

    def dumps_kml(self) -> List[dict]:
        kml_features = []

        for route_waypoint in self.waypoints:
            kml_features.append(route_waypoint.dumps_feature(route_id=self.id))

        return kml_features

    def dump_kml(self, path: Path) -> None:
        fiona.drvsupport.supported_drivers["KML"] = "rw"

        with fiona.open(
            path,
            mode="w",
            driver="KML",
            crs=crs_from_epsg(4326),
            schema=RouteWaypoint.feature_schema,
        ) as layer:
            layer.writerecords(self.dumps_kml())

    def __repr__(self) -> str:
        _start = "-"
        _end = "-"

        try:
            _start = self.first_waypoint.waypoint.designator.ljust(6)
            _end = self.last_waypoint.waypoint.designator.ljust(6)
        except AttributeError:
            pass

        return f"<Route {self.id} :- [{self.name.ljust(10, '_')}], {self.waypoints_count} waypoints, Start/End: {_start} / {_end}>"


class WaypointCollection:
    def __init__(self) -> None:
        self._waypoints: List[Waypoint] = []

    def append(self, waypoint: Waypoint) -> None:
        self._waypoints.append(waypoint)

    @property
    def waypoints(self) -> List[Waypoint]:
        return self._waypoints

    def dump_csv(self, path: Path) -> None:
        with open(path, mode="w") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=list(Waypoint.csv_schema.keys()))
            writer.writeheader()

            for waypoint in self.waypoints:
                _last_accessed_at = waypoint.last_accessed_at
                if _last_accessed_at is not None:
                    _last_accessed_at = _last_accessed_at.isoformat()

                writer.writerow(
                    {
                        "designator": waypoint.designator,
                        "latitude": waypoint.geometry.y,
                        "longitude": waypoint.geometry.x,
                        "comment": waypoint.comment,
                        "last_accessed_at": _last_accessed_at,
                        "last_accessed_by": waypoint.last_accessed_by,
                    }
                )

    def dump_kml(self, path: Path) -> None:
        fiona.drvsupport.supported_drivers["KML"] = "rw"

        with fiona.open(
            path, mode="w", driver="KML", crs=crs_from_epsg(4326), schema=Waypoint.feature_schema, layer="waypoints"
        ) as layer:
            for waypoint in self.waypoints:
                layer.write(waypoint.dumps_feature())

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

    def append(self, route: Route) -> None:
        self._routes.append(route)

    @property
    def routes(self) -> List[Route]:
        return self._routes

    def _dumps_features_all_waypoints_with_routes(self):
        _route_waypoints = []

        for route in self.routes:
            route_waypoints = route.dumps_csv()
            for route_waypoint in route_waypoints:
                _route_waypoints.append({**{"route_name": route.name}, **route_waypoint})

        return _route_waypoints

    def dump_csv(self, path: Path, separate: bool = False) -> None:
        if separate:
            for route in self.routes:
                route.dump_csv(path=path.joinpath(f"{route.name.lower()}.csv"))
        else:
            with open(path, mode="w") as output_file:
                _fieldnames = ["route_name"] + list(Route.csv_schema.keys())
                writer = csv.DictWriter(output_file, fieldnames=_fieldnames)
                writer.writeheader()
                writer.writerows(self._dumps_features_all_waypoints_with_routes())

    def dump_kml(self, path: Path, separate: bool = False) -> None:
        if separate:
            for route in self.routes:
                route.dump_kml(path=path.joinpath(f"{route.name.lower()}.kml"))
        else:
            fiona.drvsupport.supported_drivers["KML"] = "rw"

            feature_schema = {
                "geometry": "None",
                "properties": {
                    "route_name": "str",
                    "sequence": "int",
                    "designator": "str",
                    "latitude": "float",
                    "longitude": "float",
                    "description": "str",
                },
            }

            with fiona.open(
                path,
                mode="w",
                driver="KML",
                crs=crs_from_epsg(4326),
                schema=feature_schema,
            ) as layer:
                layer.writerecords(self._dumps_features_all_waypoints_with_routes())

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

    def __init__(self):
        self.waypoints: WaypointCollection = WaypointCollection()
        self.routes: RouteCollection = RouteCollection()

    def load_gpkg(self, path: Path):
        # waypoints
        with fiona.open(path, mode="r", driver="GPKG", layer="waypoints") as layer:
            for waypoint_feature in layer:
                _waypoint = Waypoint()
                _waypoint.loads_feature(feature=waypoint_feature)
                self.waypoints.append(_waypoint)

        # routes & route-waypoints
        with fiona.open(path, mode="r", driver="GPKG", layer="routes") as layer:
            for route_feature in layer:
                _route = Route()
                _route.loads_feature(feature=route_feature)
                self.routes.append(_route)
        with fiona.open(path, mode="r", driver="GPKG", layer="route_waypoints") as layer:
            # process route waypoints and group by route
            route_waypoints_by_route_id: Dict[str, List[RouteWaypoint]] = {}
            for route_waypoint_feature in layer:
                _route_waypoint = RouteWaypoint()
                _route_waypoint_feature = {"sequence": route_waypoint_feature["properties"]["sequence"]}

                _route_waypoint.loads_feature(feature=route_waypoint_feature, waypoints=self.waypoints)

                if route_waypoint_feature["properties"]["route_id"] not in route_waypoints_by_route_id.keys():
                    route_waypoints_by_route_id[route_waypoint_feature["properties"]["route_id"]] = []
                route_waypoints_by_route_id[route_waypoint_feature["properties"]["route_id"]].append(_route_waypoint)

            for route_id, route_waypoint_features in route_waypoints_by_route_id.items():
                route = self.routes[route_id]
                route.waypoints = route_waypoint_features

    def dump_gpkg(self, path: Path):
        # waypoints
        with fiona.open(
            path, mode="w", driver="GPKG", crs=crs_from_epsg(4326), schema=Waypoint.feature_schema, layer="waypoints"
        ) as layer:
            for waypoint in self.waypoints:
                layer.write(waypoint.dumps_feature())

        # route_waypoints
        with fiona.open(
            path, mode="w", driver="GPKG", schema=RouteWaypoint.feature_schema, layer="route_waypoints"
        ) as layer:
            for route in self.routes:
                for route_waypoint in route.waypoints:
                    layer.write(route_waypoint.dumps_feature(route_id=route.id))

        # routes
        # (only name and any other top/route level information is stored here, waypoints are stored in `route_waypoints`)
        with fiona.open(
            path, mode="w", driver="GPKG", crs=crs_from_epsg(4326), schema=Route.feature_schema, layer="routes"
        ) as layer:
            for route in self.routes:
                layer.write(route.dumps_feature())

    def dump_csv(self, path: Path):
        path = path.resolve()
        path.mkdir(parents=True, exist_ok=True)

        self.waypoints.dump_csv(path=path.joinpath("waypoints.csv"))
        self.routes.dump_csv(path=path.joinpath("routes.csv"))
        self.routes.dump_csv(path=path, separate=True)

    def dump_kml(self, path: Path):
        path = path.resolve()
        path.mkdir(parents=True, exist_ok=True)

        self.waypoints.dump_kml(path=path.joinpath("waypoints.kml"))
        # TODO: Resolve why this call doesn't work (collection schema order)
        # self.routes.dump_kml(path=path.joinpath("routes.kml"))
        self.routes.dump_kml(path=path, separate=True)

    def __repr__(self):
        return f"<NetworkManager : {len(self.waypoints)} Waypoints - {len(self.routes)} Routes>"
