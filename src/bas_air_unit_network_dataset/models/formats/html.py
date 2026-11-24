from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from bas_air_unit_network_dataset.utils import convert_coordinate_dd_2_ddm_padded

if TYPE_CHECKING:
    from datetime import date

    from bas_air_unit_network_dataset.models.base.waypoint import Waypoint as BaseWaypoint


@dataclass
class WaypointsReportWaypoint:
    """Waypoint in the Waypoints Report."""

    _placeholder: ClassVar[str] = "-"

    id: str
    lon: float
    lat: float
    name: str = _placeholder
    colocated_with: str = _placeholder
    last_accessed_at: date | None = None
    last_accessed_by: str = _placeholder
    fuel: int | None = None
    elevation_ft: int | None = None
    comment: str = _placeholder
    category: str | None = None

    def __post_init__(self) -> None:
        """Post-initialisation validation and processing."""
        ddm_padded_x, ddm_padded_y = convert_coordinate_dd_2_ddm_padded(lon=self.lon, lat=self.lat)
        self.lon_ddm_padded = ddm_padded_x
        self.lat_ddm_padded = ddm_padded_y
        self.last_accessed_at_fmt = self.last_accessed_at.strftime("%Y-%b-%d").upper() if self.last_accessed_at else "-"
        self.fuel_fmt = str(self.fuel) if self.fuel is not None else "-"
        self.elevation_ft_fmt = str(self.elevation_ft) if self.elevation_ft is not None else "-"

    @classmethod
    def loads(cls, waypoint: BaseWaypoint) -> Self:
        """Load a base waypoint as a Waypoints Report waypoint."""
        return cls(
            id=waypoint.identifier,
            lon=waypoint.geometry.x,
            lat=waypoint.geometry.y,
            name=waypoint.name or WaypointsReportWaypoint._placeholder,
            colocated_with=waypoint.colocated_with or WaypointsReportWaypoint._placeholder,
            last_accessed_at=waypoint.last_accessed_at,
            last_accessed_by=waypoint.last_accessed_by or WaypointsReportWaypoint._placeholder,
            fuel=waypoint.fuel,
            elevation_ft=waypoint.elevation_ft,
            comment=waypoint.comment or WaypointsReportWaypoint._placeholder,
            category=waypoint.category,
        )
