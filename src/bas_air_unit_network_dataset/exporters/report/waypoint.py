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
    name: Optional[str] = None
    colocated_with: Optional[str] = None
    last_accessed_at: Optional[date] = None
    last_accessed_by: Optional[str] = None
    fuel: Optional[int] = None
    elevation_ft: Optional[int] = None
    comment: Optional[str] = None
    category: Optional[str] = None

    def __post_init__(self) -> None:
        if isinstance(self.last_accessed_at, date):
            self.last_accessed_at_fmt = self.last_accessed_at.strftime("%Y-%b-%d").upper()

        geometry_ddm = convert_coordinate_dd_2_ddm_padded(lon=self.geometry.x, lat=self.geometry.y)
        self.lat_ddm_padded = geometry_ddm["lat"]
        self.lon_ddm_padded = geometry_ddm["lon"]
