from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from shapely.geometry.point import Point

from bas_air_unit_network_dataset.utils import convert_coordinate_dd_2_ddm_padded


@dataclass
class WaypointsReportWaypoint:
    """
    Waypoints Report waypoint.

    Concrete representation of an abstract waypoint for use in the Waypoints Report PDF.
    """

    id: str
    geometry: Point
    name: Optional[str] = "-"
    colocated_with: Optional[str] = "-"
    last_accessed_at: Optional[date] = None
    last_accessed_by: Optional[str] = "-"
    fuel: Optional[int] = None
    elevation_ft: Optional[int] = None
    comment: Optional[str] = "-"
    category: Optional[str] = None

    def __post_init__(self) -> None:
        self.geometry_ddm = convert_coordinate_dd_2_ddm_padded(lon=self.geometry.x, lat=self.geometry.y)

        if self.name is None:
            self.name = "-"
        if self.colocated_with is None:
            self.colocated_with = "-"
        if self.last_accessed_by is None:
            self.last_accessed_by = "-"
        if self.comment is None:
            self.comment = "-"

    @property
    def lat_ddm_padded(self) -> str:
        """Latitude as padded DDM."""
        return self.geometry_ddm["lat"]

    @property
    def lon_ddm_padded(self) -> str:
        """Longitude as padded DDM."""
        return self.geometry_ddm["lon"]

    @property
    def last_accessed_at_fmt(self) -> str:
        """Formatted last accessed at value based on type."""
        if self.last_accessed_at is None:
            return "-"
        if isinstance(self.last_accessed_at, date):
            return self.last_accessed_at.strftime("%Y-%b-%d").upper()
        msg = "Invalid date format."
        raise ValueError(msg)

    @property
    def fuel_fmt(self) -> str:
        """Formatted fuel value."""
        if self.fuel is None:
            return "-"
        return str(self.fuel)

    @property
    def elevation_ft_fmt(self) -> str:
        """Formatted elevation_ft value."""
        if self.elevation_ft is None:
            return "-"
        return str(self.elevation_ft)
