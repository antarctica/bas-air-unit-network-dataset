from dataclasses import dataclass
from typing import ClassVar, Self

from bas_air_unit_network_dataset.models.base.waypoint import Waypoint as BaseWaypoint
from bas_air_unit_network_dataset.utils import convert_coordinate_dd_2_ddm


@dataclass
class Waypoint:
    """Waypoint for use in a CSV file."""

    _placeholder: ClassVar[str] = "-"

    identifier: str
    latitude_dd: float
    longitude_dd: float
    name: str = _placeholder
    colocated_with: str = _placeholder
    last_accessed_at: str = _placeholder
    last_accessed_by: str = _placeholder
    fuel: str = _placeholder
    elevation_ft: str = _placeholder
    comment: str = _placeholder
    category: str = _placeholder

    def __post_init__(self) -> None:
        """Post-initialisation validation and processing."""
        geometry_ddm = convert_coordinate_dd_2_ddm(lon=self.longitude_dd, lat=self.latitude_dd)
        self._latitude_ddm = geometry_ddm[1]
        self._longitude_ddm = geometry_ddm[0]

    @classmethod
    def loads(cls, waypoint: BaseWaypoint) -> Self:
        """Load a base waypoint as a CSV waypoint."""
        return Waypoint(
            identifier=waypoint.identifier,
            name=waypoint.name,
            colocated_with=waypoint.colocated_with,
            latitude_dd=waypoint.geometry.y,
            longitude_dd=waypoint.geometry.x,
            last_accessed_at=waypoint.last_accessed_at.isoformat() if waypoint.last_accessed_at else None,
            last_accessed_by=waypoint.last_accessed_by,
            fuel=waypoint.fuel,
            elevation_ft=waypoint.elevation_ft,
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
            "latitude_ddm": self._latitude_ddm,
            "longitude_ddm": self._longitude_ddm,
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
