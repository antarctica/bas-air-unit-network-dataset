import csv
from collections import OrderedDict
from datetime import date
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union

import fiona
import ulid
from fiona.crs import from_epsg as crs_from_epsg
from gpxpy import parse as gpx_parse
from gpxpy.gpx import GPX, GPXRoute, GPXRoutePoint, GPXWaypoint
from shapely.geometry import Point

from bas_air_unit_network_dataset.exporters.fpl import (
    Fpl,
    Route as FplRoute,
    RoutePoint as FplRoutePoint,
    Waypoint as FplWaypoint,
)
from bas_air_unit_network_dataset.utils import convert_coordinate_dd_2_ddm, file_name_with_date


class Waypoint:
    """
    A known location with a specified identifier.

    Waypoints identify locations relevant to navigation, typically as part of a network of waypoints (locations) and
    routes (represented by the Route class). Waypoints may be used in any number of routes, any number of times.
    Waypoints do not need to be part of any routes, and are not aware of any routes they are part of.

    Waypoints are geographic features with a point geometry and attributes including an identifier, name, an optional
    description and other information.

    This class is an abstract representation of a waypoint concept, independent of any specific formats or encodings.
    However, to ensure key waypoint information can be represented using all supported formats and encodings, this class
    applies the most restrictive limitations of supported formats and encodings.

    See the 'Information Model' section of the library README for more information.
    """

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
        name: Optional[str] = None,
        colocated_with: Optional[str] = None,
        last_accessed_at: Optional[date] = None,
        last_accessed_by: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        """
        Create or load a waypoint, optionally setting parameters.

        Waypoints will be assigned a unique and persistent feature ID automatically.

        :type identifier: str
        :param identifier: unique reference for waypoint
        :type lon: float
        :param lon: longitude component of waypoint geometry
        :type lat: float
        :param lat: latitude component of waypoint geometry
        :type name: str
        :param name: optionally, waypoint name/summary
        :type colocated_with: str
        :param colocated_with: optionally, things near waypoint, or other names waypoint is known as
        :type last_accessed_at: date
        :param last_accessed_at: optionally, the date waypoint was last accessed
        :type last_accessed_by: str
        :param last_accessed_by: optionally, identifier of last agent to access waypoint.
        :type comment: str
        :param comment: free-text descriptive comment for waypoint
        """
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

        if lon is not None or lat is not None:
            self.geometry = [lon, lat]

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
    def fid(self) -> str:
        """
        Waypoint feature ID.

        A unique and typically persistent value.

        :rtype: str
        :return: feature ID
        """
        return self._id

    @fid.setter
    def fid(self, _id: str) -> None:
        """
        Set waypoint feature ID.

        This is only intended to be used where an existing waypoint is being loaded, as new waypoints will be assigned a
        feature ID automatically.

        Typically, a persistent, but otherwise unique, value but which may not be recognisable by humans.

        :type _id: str
        :param _id: feature ID
        """
        self._id = str(ulid.from_str(_id))

    @property
    def identifier(self) -> str:
        """
        Waypoint identifier.

        Unique value identifying waypoint.

        :rtype: str
        :return: unique reference for waypoint
        """
        return self._identifier

    @identifier.setter
    def identifier(self, identifier: str) -> None:
        """
        Set waypoint identifier.

        Identifiers must be unique values (across other waypoints) and should be formally controlled. Identifiers must
        be 6 characters or fewer. This limit comes from the Garmin FPL standard and ensures values can be consistently
        and unambiguously represented across all supported standards.

        The name property can be used for setting a less controlled and longer value.

        E.g. if a waypoint has an identifier 'FOXTRT' (to fit the six-character limit), the name can be 'FOXTROT' or
        'Foxtrot'.

        :type identifier: str
        :param identifier: waypoint identifier
        """
        if len(identifier) > Waypoint.identifier_max_length:
            raise ValueError(f"Identifiers must be 6 characters or less. {identifier!r} is {len(identifier)}.")

        self._identifier = identifier

    @property
    def geometry(self) -> Point:
        """
        Waypoint geometry.

        Geometries use the EPSG:4326 CRS.

        :rtype: Point
        :return: waypoint geometry
        """
        return self._geometry

    @geometry.setter
    def geometry(self, geometry: List[float]) -> None:
        """
        Set waypoint geometry.

        Values should be in [longitude, latitude] axis order using the EPSG:4326 CRS.

        :type geometry: list
        :param geometry: waypoint geometry as a list of longitude/latitude values
        """
        lon = geometry[0]
        lat = geometry[1]

        if -180 > lon > 180:
            raise ValueError("Longitude must be between -180 and +180.")
        if -90 > lat > 90:
            raise ValueError("Latitude must be between -90 and +90.")

        self._geometry = Point(lon, lat)

    @property
    def name(self) -> Optional[str]:
        """
        Waypoint name.

        Optional longer and/or less formal name for waypoint.

        E.g. if a waypoint has an identifier 'FOXTRT' (to fit the six-character limit), the name could be 'FOXTROT' or
        'Foxtrot'.

        Returns `None` if name unknown.

        :rtype: str
        :return: waypoint name/summary
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Set waypoint name.

        Names are typically less formal/controlled versions of identifiers, with a higher allowed length of 17
        characters (inc. spaces). This limit comes from the Garmin FPL standard and ensures values can be consistently
        and unambiguously represented across all supported standards.

        E.g. if a waypoint has an identifier 'FOXTRT' (to fit the six-character limit), the name can be 'FOXTROT' or
        'Foxtrot'.

        :type name: str
        :param name: waypoint name/summary
        """
        if len(name) > Waypoint.name_max_length:
            raise ValueError(f"Names must be 17 characters or less. {name!r} is {len(name)}.")

        self._name = name

    @property
    def colocated_with(self) -> Optional[str]:
        """
        What waypoint is near or also known as by others.

        Returns `None` if date unknown. Values are free text and unstructured.

        :rtype: str
        :return: things near waypoint, or other names waypoint is known as
        """
        return self._colocated_with

    @colocated_with.setter
    def colocated_with(self, colocated_with: str) -> None:
        """
        Set what waypoint is near or also known as by others.

        For example a waypoint may be used as the reference for an instrument, or might be referred to as something
        else by another team or project. This value is free text and unstructured.

        :type: str
        :param colocated_with: things near waypoint, or other names waypoint is known as
        """
        self._colocated_with = colocated_with

    @property
    def last_accessed_at(self) -> Optional[date]:
        """
        When was waypoint last accessed, if known.

        Returns `None` if date unknown.

        :rtype: date
        :return: the date waypoint was last accessed
        """
        return self._last_accessed_at

    @last_accessed_at.setter
    def last_accessed_at(self, _date: date) -> None:
        """
        Set when waypoint was last accessed.

        :type _date: date
        :param _date: the date waypoint was last accessed
        """
        self._last_accessed_at = _date

    @property
    def last_accessed_by(self) -> Optional[str]:
        """
        Who last accessed waypoint, if known.

        Returns `None` if identity unknown.

        :rtype: str
        :return: identifier of last agent to access waypoint, if known
        """
        return self._last_accessed_by

    @last_accessed_by.setter
    def last_accessed_by(self, last_accessed_by: str) -> None:
        """
        Set who last accessed waypoint.

        Values may use any scheme (call signs, initials, usernames, etc.) but should ideally come from a controlled
        list for consistency and auditing.

        :param last_accessed_by: identifier of last agent to access waypoint.
        """
        self._last_accessed_by = last_accessed_by

    @property
    def comment(self) -> Optional[str]:
        """
        Waypoint comment.

        :rtype: str
        :return: free-text descriptive comment for waypoint
        """
        return self._comment

    @comment.setter
    def comment(self, comment: str) -> None:
        """
        Set waypoint comment.

        :type comment: str
        :param comment: free-text descriptive comment for waypoint
        """
        self._comment = comment

    def loads_feature(self, feature: dict) -> None:
        """
        Create a Waypoint from a generic feature.

        :type feature: dict
        :param feature: feature representing a Waypoint
        """
        self.fid = feature["properties"]["id"]
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
        """
        Build waypoint geometry for use in a generic feature.

        :rtype: dict
        :return: Waypoint geometry
        """
        geometry = {"type": "Point", "coordinates": (self.geometry.x, self.geometry.y)}
        if self.geometry.has_z:
            geometry["coordinates"] = (self.geometry.x, self.geometry.y, self.geometry.z)

        return geometry

    def dumps_feature(self, inc_spatial: bool = True) -> dict:
        """
        Build waypoint as a generic feature for further processing.

        :type inc_spatial: bool
        :param inc_spatial: whether to include the geometry of the route and/or route waypoints in generated features
        :rtype: dict
        :return: feature for waypoint
        """
        feature = {
            "geometry": None,
            "properties": {
                "id": self.fid,
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
        """
        Build CSV data for waypoint.

        :type inc_dd_lat_lon: bool
        :param inc_dd_lat_lon: include latitude and longitude columns in decimal degree format
        :type inc_ddm_lat_lon: bool
        :param inc_ddm_lat_lon: include latitude and longitude columns in degrees decimal minutes format
        :rtype: dict
        :return: row of generated CSV data for waypoint
        """
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
        """
        Build a GPX element for waypoint.

        These elements are intended to be combined into FPL documents elsewhere.

        As the GPX standard does not have properties defined for attributes such as name and/or last accessed at, they
        are concatenated as part of the free-text description field.

        :rtype: GPXWaypoint
        :return: generated GPX element for waypoint
        """
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
        """
        Build a FPL element for waypoint.

        These elements are intended to be combined into FPL documents elsewhere.

        The FPL waypoint type is hard-coded to user defined waypoints as other types are not intended to be produced by
        this library.

        The FPL country code is hard-coded to a conventional value used by the BAS Air Unit for Antarctica. This will
        be reviewed in #157.

        :rtype: FplWaypoint
        :return: generated FPL element for waypoint
        """
        waypoint = FplWaypoint()

        waypoint.identifier = self.identifier
        waypoint.waypoint_type = "USER WAYPOINT"
        waypoint.country_code = "__"
        waypoint.longitude = self.geometry.x
        waypoint.latitude = self.geometry.y

        if self.name is not None:
            waypoint.comment = self.name

        return waypoint

    def __repr__(self) -> str:
        """String representation of a Waypoint."""
        return f"<Waypoint {self.fid} :- [{self.identifier.ljust(6, '_')}], {self.geometry}>"


class RouteWaypoint:
    """
    A Waypoint within a Route.

    Route waypoints link a particular Waypoint to a particular Route, including contextual information on where with
    the route a waypoint appears (i.e. at the beginning, end or somewhere inbetween).

    This class handles singular waypoints/positions within a route. All waypoints and positions within a route are
    managed by the Route class.

    See the 'Information Model' section of the library README for more information.
    """

    feature_schema = {
        "geometry": "None",
        "properties": {"route_id": "str", "waypoint_id": "str", "sequence": "int"},
    }

    feature_schema_spatial = {
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
            raise ValueError("A `sequence` value must be provided if `waypoint` is set.")
        elif waypoint is None and sequence is not None:
            raise ValueError("A `waypoint` value must be provided if `sequence` is set.")
        elif waypoint is not None and sequence is not None:
            self.waypoint = waypoint
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

    def loads_feature(self, feature: dict, waypoints: "WaypointCollection") -> None:
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
            raise KeyError(
                f"Waypoint with ID {feature['properties']['waypoint_id']!r} not found in available waypoints."
            ) from e

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

    def dumps_csv(self, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> Dict[str, str]:
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

        route_waypoint = {**route_waypoint, **waypoint}

        return route_waypoint

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
        self._waypoints: List[RouteWaypoint] = []

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
    def waypoints(self) -> List[RouteWaypoint]:
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
    def waypoints(self, route_waypoints: List[RouteWaypoint]) -> None:
        """
        Set waypoints within route.

        Typically, there are at least two waypoints, representing a start and end of the route.

        Waypoints to be added must use the RouteWaypoint class as a wrapper around Waypoint objects.

        Note this method will replace any existing waypoints within the route.

        :type route_waypoints: list
        :param route_waypoints: waypoints that make up route
        """
        self._waypoints = route_waypoints

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
    ) -> List[dict]:
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
    ) -> List[dict]:
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
        with open(path, mode="w", newline="", encoding="utf-8-sig") as output_file:
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
        with open(path, mode="w") as gpx_file:
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
            route_point = FplRoutePoint()
            route_point.waypoint_identifier = route_waypoint.waypoint.identifier
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
        with open(path, mode="w") as xml_file:
            xml_file.write(self.dumps_fpl(flight_plan_index=flight_plan_index).dumps_xml().decode())

    def __repr__(self) -> str:
        """String representation of a Route."""
        start = "-"
        end = "-"

        try:
            start = self.first_waypoint.waypoint.identifier.ljust(6)
            end = self.last_waypoint.waypoint.identifier.ljust(6)
        except AttributeError:
            pass

        return f"<Route {self.fid} :- [{self.name.ljust(10, '_')}], {self.waypoints_count} waypoints, Start/End: {start} / {end}>"


class WaypointCollection:
    """
    A collection of Waypoints.

    Provides a dictionary like interface to managing Waypoints, along with methods for managing multiple Waypoints at
    once.
    """

    def __init__(self) -> None:
        """Create routes collection."""
        self._waypoints: List[Waypoint] = []

    @property
    def waypoints(self) -> List[Waypoint]:
        """
        Get all waypoints in collection as Waypoint classes.

        :rtype: list
        :return: routes in collection as Waypoint classes
        """
        return self._waypoints

    def append(self, waypoint: Waypoint) -> None:
        """
        Add waypoint to collection.

        For consistency waypoints are sorted by identifier.

        :type waypoint: Waypoint
        :param waypoint: additional waypoint
        """
        self._waypoints.append(waypoint)
        self._waypoints = sorted(self.waypoints, key=lambda x: x.identifier)

    def lookup(self, identifier: str) -> Optional[Waypoint]:
        """
        Get waypoint in collection specified by waypoint identifier.

        Returns `None` if no matching waypoint found.

        :type identifier: str
        :param identifier: waypoint identifier
        :rtype: Waypoint
        :return: specified waypoint, or None if no match
        """
        for waypoint in self._waypoints:
            if waypoint.identifier == identifier:
                return waypoint

        return None

    def dump_features(self, inc_spatial: bool = True) -> List[dict]:
        """
        Build all waypoints in collection as generic features for further processing.

        This method is a wrapper around the `dumps_feature()` method for each waypoint.

        :type inc_spatial: bool
        :param inc_spatial: whether to include the geometry of each waypoint in generated features
        :rtype: list
        :return: features for each waypoint in collection
        """
        features = []

        for waypoint in self.waypoints:
            features.append(waypoint.dumps_feature(inc_spatial=inc_spatial))

        return features

    def dump_csv(self, path: Path, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> None:
        """
        Write waypoints as a CSV file for further processing and/or visualisation.

        :type path: path
        :param path: Output path
        :type inc_dd_lat_lon: bool
        :param inc_dd_lat_lon: include latitude and longitude columns in decimal degree format
        :type inc_ddm_lat_lon: bool
        :param inc_ddm_lat_lon: include latitude and longitude columns in degrees decimal minutes format
        """
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
        with open(path, mode="w", newline="", encoding="utf-8-sig") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()

            for waypoint in self.waypoints:
                writer.writerow(waypoint.dumps_csv(inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon))

    def dumps_gpx(self) -> GPX:
        """
        Build a GPX document for all waypoints within collection.

        :rtype: GPX
        :return: generated GPX file containing all waypoints in collection
        """
        gpx = GPX()

        for waypoint in self.waypoints:
            gpx.waypoints.append(waypoint.dumps_gpx())

        return gpx

    def dump_gpx(self, path: Path) -> None:
        """
        Write waypoints as a GPX file for use in GPS devices.

        :type path: path
        :param path: Output path
        """
        with open(path, mode="w") as gpx_file:
            gpx_file.write(self.dumps_gpx().to_xml())

    def dumps_fpl(self) -> Fpl:
        """
        Build a FPL document for all waypoints within collection.

        :rtype: FPL
        :return: generated FPL file containing all waypoints in collection
        """
        fpl = Fpl()

        for waypoint in self.waypoints:
            fpl.waypoints.append(waypoint.dumps_fpl())

        fpl.validate()

        return fpl

    def dump_fpl(self, path: Path) -> None:
        """
        Write waypoints as a FPL file for use in aircraft GPS devices.

        :type path: path
        :param path: Output path
        """
        fpl = self.dumps_fpl()
        fpl.dump_xml(path=path)

    def __getitem__(self, _id: str) -> Waypoint:
        """
        Get a waypoint by its ID.

        :type _id: Waypoint
        :param _id: a waypoint ID (distinct from a waypoint's Identifier)
        :rtype Waypoint
        :return: specified Waypoint

        :raises KeyError: if no Waypoint exists with the requested ID
        """
        for waypoint in self._waypoints:
            if waypoint.fid == _id:
                return waypoint

        raise KeyError(_id)

    def __iter__(self) -> Iterator[Waypoint]:
        """Iterate through each Waypoint within WaypointCollection."""
        return self._waypoints.__iter__()

    def __len__(self) -> int:
        """Number of Waypoints within WaypointCollection."""
        return len(self.waypoints)

    def __repr__(self) -> str:
        """String representation of a WaypointCollection."""
        return f"<WaypointCollection : {self.__len__()} waypoints>"


class RouteCollection:
    """
    A collection of Routes.

    Provides a dictionary like interface to managing Routes, along with methods for managing multiple Routes at once.
    """

    def __init__(self) -> None:
        """Create routes collection."""
        self._routes: List[Route] = []

    @property
    def routes(self) -> List[Route]:
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
    ) -> List[dict]:
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
                inc_spatial=inc_spatial, inc_waypoints=True, inc_route_id=inc_route_id, inc_route_name=inc_route_name
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
        Writes all routes to a single CSV file for further processing and/or visualisation.

        :type path: path
        :param path: Output path
        :type inc_dd_lat_lon: bool
        :param inc_dd_lat_lon: include latitude and longitude columns in decimal degree format
        :type inc_ddm_lat_lon: bool
        :param inc_ddm_lat_lon: include latitude and longitude columns in degrees decimal minutes format
        """
        fieldnames: List[str] = ["route_name"] + list(Route.csv_schema_waypoints.keys())

        route_waypoints: List[dict] = []
        for route in self.routes:
            route_waypoints += route.dumps_csv(
                inc_waypoints=True, route_column=True, inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon
            )

        # newline parameter needed to avoid extra blank lines in files on Windows [#63]
        with open(path, mode="w", newline="", encoding="utf-8-sig") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(route_waypoints)

    def dump_csv(
        self, path: Path, separate_files: bool = False, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False
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
            self._dump_csv_separate(path=path, inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon)
        else:
            self._dump_csv_combined(path=path, inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon)

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
            route.dump_gpx(path=path.joinpath(f"{route.name.upper()}.gpx"), inc_waypoints=inc_waypoints)

    def _dump_gpx_combined(self, path: Path) -> None:
        """
        Writes all routes to a single GPX file for use in GPS devices.

        :type path: path
        :param path: Output path
        """
        with open(path, mode="w") as gpx_file:
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
            return None

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
            raise RuntimeError("FPL does not support combined routes, `separate_files` must be set to True.")

        flight_plan_index = 1
        for route in self.routes:
            route.dump_fpl(path=path.joinpath(f"{route.name.upper()}.fpl"), flight_plan_index=flight_plan_index)
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
        """Number of Routes within RouteCollection."""
        return len(self.routes)

    def __repr__(self) -> str:
        """String representation of an RouteCollection."""
        return f"<RouteCollection : {self.__len__()} routes>"


class NetworkManager:
    # If you can come up with a better name for this class, you could win a prize!
    """
    A collection of Routes and Waypoints that form a network.

    It provides methods for importing and exporting route and waypoint information in various formats using a
    defined file naming and directory structure, which is specific to the BAS Air Unit.
    """

    def __init__(self, dataset_path: Path, output_path: Optional[Path] = None, init: Optional[bool] = False) -> None:
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
                raise FileNotFoundError("Output path does not exist.")
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
            raise FileNotFoundError("No output path specified")

        path = path.resolve()
        if fmt_dir is not None:
            path = path.joinpath(fmt_dir)

        path.mkdir(parents=True, exist_ok=True)

        if not path.exists():
            raise FileNotFoundError("Output path does not exist.")

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
        """
        Read routes and waypoints from a GPX file.

        This method parses any routes and/or waypoints from the input file, updating collections in this class and
        persisting the data to the configured GeoPackage.

        :type path: Path
        :param path: input GPX file path
        """
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
            path=path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}.csv")), inc_ddm_lat_lon=True
        )
        self.waypoints.dump_csv(
            path=path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}_DD.csv")), inc_dd_lat_lon=True
        )
        # combined/individual routes files omitted as they aren't needed by the Air Unit (#101)

    def dump_gpx(self, path: Optional[Path] = None) -> None:
        """
        Write routes and waypoints as GPX files for use in GPS devices.

        This method builds a network wide GPX file using the `dumps_gpx()` methods for routes and waypoints.

        # waypoints and combined/individual routes files omitted as they aren't needed by the Air Unit (#101)
        Files and directories currently use BAS Air Unit specific naming conventions - this will be addressed in #46.

        A GPX file containing all waypoints and a GPX for each route would normally be generated, but as they are not
        needed by BAS Air Unit they are currently disabled - this will be addressed in #46.

        :type path: Path
        :param path: base path for exported files
        """
        path = self._get_output_path(path=path, fmt_dir="GPX")

        # `network.gpx` needs access to both routes and waypoints so needs to be done at this level
        gpx = GPX()
        gpx.waypoints = self.waypoints.dumps_gpx().waypoints
        gpx.routes = self.routes.dumps_gpx().routes
        with open(path.joinpath(file_name_with_date("00_NETWORK_{{date}}.gpx")), mode="w") as gpx_file:
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
        """String representation of a NetworkManager."""
        return f"<NetworkManager : {len(self.waypoints)} Waypoints - {len(self.routes)} Routes>"
