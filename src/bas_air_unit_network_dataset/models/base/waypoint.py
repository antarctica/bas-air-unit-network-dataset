from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import ClassVar, Self

from geojson.feature import Feature
from shapely.geometry import Point


@dataclass
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

    Properties:
    - `identifier`: identifier, a unique value identifying waypoint
    - `lon`: longitude component of waypoint geometry
    - `lat`: latitude component of waypoint geometry
    - `name`: optional, longer and/or less formal value identifying waypoint (e.g. 'Foxtrot' for identifier: 'FOXTRT')
    - `colocated_with`: optional, things near waypoint, or other names waypoint is known as (freetext structure)
    - `last_accessed_at`: optional, date waypoint was last accessed by an agent
    - `last_accessed_by`: optional, identifier of last agent to access waypoint (freetext value)
    - `fuel`: optional, fuel quantity at waypoint (non-negative value, None if unknown)
    - `elevation_ft`: optional, waypoint elevation in feet (non-negative value, None if unknown)
    - `comment`: optional, descriptive comment for waypoint (freetext value)
    - `category`: optional, single uncontrolled grouping label for waypoint used for categorisation

    See the 'Information Model' section of the library README for more information.
    """

    _identifier_max_length: ClassVar[int] = 6
    _name_max_length: ClassVar[int] = 17

    identifier: str
    lon: float
    lat: float
    name: str | None = None
    colocated_with: str | None = None
    last_accessed_at: date | None = None
    last_accessed_by: str | None = None
    fuel: int | None = None
    elevation_ft: int | None = None
    comment: str | None = None
    category: str | None = None

    def __post_init__(self) -> None:
        """Post-initialisation validation and processing."""
        if not -180 <= self.lon <= 180:
            msg = "Longitude must be between -180 and +180."
            raise ValueError(msg) from None
        if not -90 <= self.lat <= 90:
            msg = "Latitude must be between -90 and +90."
            raise ValueError(msg) from None

        if len(self.identifier) > self._identifier_max_length:
            msg = f"Identifiers must be {self._identifier_max_length} characters or less. {self.identifier!r} is {len(self.identifier)}."
            raise ValueError(msg) from None
        if self.name and len(self.name) > Waypoint._name_max_length:
            msg = f"Names must be {self._name_max_length} characters or less. {self.name!r} is {len(self.name)}."
            raise ValueError(msg) from None

        if (self.last_accessed_at and not self.last_accessed_by) or (
            self.last_accessed_by and not self.last_accessed_at
        ):
            msg = "Both `last_accessed_at` and `last_accessed_by` must be set together."
            raise ValueError(msg) from None

        if self.fuel is not None and self.fuel < 0:
            msg = f"Fuel must be a non-negative integer {self.fuel!r} is not."
            raise ValueError(msg) from None
        if self.elevation_ft is not None and self.elevation_ft < 0:
            msg = f"Elevation must be a non-negative integer {self.elevation_ft!r} is not."
            raise ValueError(msg) from None

    def __repr__(self) -> str:
        """String representation."""
        return f"<Waypoint {self.identifier.ljust(6, '_')} :- {self.geometry}>"

    @property
    def geometry(self) -> Point:
        """
        Waypoint geometry.

        Geometries use the EPSG:4326 CRS.
        """
        if self.elevation_ft is not None:
            return Point(self.lon, self.lat, self.elevation_ft * 0.3048)
        return Point(self.lon, self.lat)

    @classmethod
    def loads_feature(cls, feature: Feature) -> Self:
        """Create a Waypoint from a GeoJSON point feature."""
        return Waypoint(
            lon=feature.geometry.coordinates[0],
            lat=feature.geometry.coordinates[1],
            identifier=feature.properties["identifier"],
            name=feature.properties.get("name"),
            colocated_with=feature.properties.get("colocated_with"),
            last_accessed_at=date.fromisoformat(feature.properties["last_accessed_at"])
            if feature.properties.get("last_accessed_at") is not None
            else None,
            last_accessed_by=feature.properties.get("last_accessed_by"),
            fuel=feature.properties.get("fuel"),
            elevation_ft=feature.properties.get("elevation_ft"),
            comment=feature.properties.get("comment"),
            category=feature.properties.get("category"),
        )
