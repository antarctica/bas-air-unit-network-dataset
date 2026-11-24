from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from bas_air_unit_network_dataset.utils import convert_coordinate_dd_2_ddm

if TYPE_CHECKING:
    from bas_air_unit_network_dataset.models.base.waypoint import Waypoint as BaseWaypoint


@dataclass
class Waypoint:
    """Waypoint for use in a CSV file."""

    _placeholder: ClassVar[str] = "-"

    identifier: str
    latitude_dd: float
    longitude_dd: float
    name: str | None = _placeholder
    colocated_with: str | None = _placeholder
    last_accessed_at: str | None = _placeholder
    last_accessed_by: str | None = _placeholder
    fuel: str | None = _placeholder
    elevation_ft: str | None = _placeholder
    comment: str | None = _placeholder
    category: str | None = _placeholder

    def __post_init__(self) -> None:
        """Post-initialisation validation and processing."""
        geometry_ddm = convert_coordinate_dd_2_ddm(lon=self.longitude_dd, lat=self.latitude_dd)
        self.latitude_ddm = geometry_ddm[1]
        self.longitude_ddm = geometry_ddm[0]
        self.elevation_ft = self.elevation_ft or self._placeholder
        self.name = self.name or self._placeholder
        self.colocated_with = self.colocated_with or self._placeholder
        self.last_accessed_at = self.last_accessed_at or self._placeholder
        self.last_accessed_by = self.last_accessed_by or self._placeholder
        self.fuel = self.fuel or self._placeholder
        self.comment = self.comment or self._placeholder
        self.category = self.category or self._placeholder

    @classmethod
    def loads(cls, waypoint: BaseWaypoint) -> Self:
        """Load a base waypoint as a CSV waypoint."""
        return cls(
            identifier=waypoint.identifier,
            name=waypoint.name,
            colocated_with=waypoint.colocated_with,
            latitude_dd=waypoint.geometry.y,
            longitude_dd=waypoint.geometry.x,
            last_accessed_at=waypoint.last_accessed_at.isoformat() if waypoint.last_accessed_at else None,
            last_accessed_by=waypoint.last_accessed_by,
            fuel=str(waypoint.fuel) if waypoint.fuel else None,
            elevation_ft=str(waypoint.elevation_ft) if waypoint.elevation_ft else None,
            comment=waypoint.comment,
            category=waypoint.category,
        )

    def dumps(self, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> dict:
        """
        Build a row dict for a CSV waypoint.

        Where `inc_dd_lat_lon` is True, lat/lon columns are included in decimal degrees.
        Where `inc_ddm_lat_lon` is True, lat/lon columns use degrees decimal minutes format.
        """
        feature = {
            "identifier": self.identifier,
            "name": self.name,
            "colocated_with": self.colocated_with,
            "latitude_dd": self.latitude_dd,
            "longitude_dd": self.longitude_dd,
            "latitude_ddm": self.latitude_ddm,
            "longitude_ddm": self.longitude_ddm,
            "last_accessed_at": self.last_accessed_at,
            "last_accessed_by": self.last_accessed_by,
            "fuel": self.fuel,
            "elevation_ft": self.elevation_ft,
            "comment": self.comment,
            "category": self.category,
        }
        if not inc_dd_lat_lon:
            del feature["latitude_dd"]
            del feature["longitude_dd"]
        if not inc_ddm_lat_lon:
            del feature["latitude_ddm"]
            del feature["longitude_ddm"]
        return feature
