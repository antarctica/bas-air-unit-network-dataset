from __future__ import annotations

from datetime import date
from typing import ClassVar, Optional

import ulid
from gpxpy.gpx import GPXWaypoint
from shapely.geometry import Point

from bas_air_unit_network_dataset.exporters.fpl.waypoint import Waypoint as FplWaypoint
from bas_air_unit_network_dataset.utils import convert_coordinate_dd_2_ddm


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

    feature_schema_spatial: ClassVar[dict] = {
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

    csv_schema: ClassVar[dict] = {
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

        if (last_accessed_at is not None and last_accessed_by is None) or (
            last_accessed_at is None and last_accessed_by is not None
        ):
            msg = "A `last_accessed_at` and `last_accessed_by` value must be provided."
            raise ValueError(msg)

        self._last_accessed_at = last_accessed_at
        self._last_accessed_by = last_accessed_by

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
            msg = f"Identifiers must be 6 characters or less. {identifier!r} is {len(identifier)}."
            raise ValueError(msg)

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
    def geometry(self, geometry: list[float]) -> None:
        """
        Set waypoint geometry.

        Values should be in [longitude, latitude] axis order using the EPSG:4326 CRS.

        :type geometry: list
        :param geometry: waypoint geometry as a list of longitude/latitude values
        """
        lon = geometry[0]
        lat = geometry[1]

        if -180 > lon > 180:
            msg = "Longitude must be between -180 and +180."
            raise ValueError(msg)
        if -90 > lat > 90:
            msg = "Latitude must be between -90 and +90."
            raise ValueError(msg)

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
            msg = f"Names must be 17 characters or less. {name!r} is {len(name)}."
            raise ValueError(msg)

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
            msg = "A `last_accessed_by` value must be provided if `last_accessed_at` is set."
            raise ValueError(msg)
        if feature["properties"]["last_accessed_at"] is None and feature["properties"]["last_accessed_by"] is not None:
            msg = "A `last_accessed_at` value must be provided if `last_accessed_by` is set."
            raise ValueError(msg)
        if (
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
            geometry["coordinates"] = (
                self.geometry.x,
                self.geometry.y,
                self.geometry.z,
            )

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
        waypoint.description = self.name

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
            waypoint.comment = self.name.upper()

        return waypoint

    def __repr__(self) -> str:
        """Represent Waypoint as a string."""
        return f"<Waypoint {self.fid} :- [{self.identifier.ljust(6, '_')}], {self.geometry}>"
