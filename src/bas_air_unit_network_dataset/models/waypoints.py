from __future__ import annotations

import csv
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from gpxpy.gpx import GPX, GPXWaypoint
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from bas_air_unit_network_dataset.exporters.fpl.fpl import Fpl
from bas_air_unit_network_dataset.exporters.report.waypoint import WaypointsReportWaypoint
from bas_air_unit_network_dataset.models.categories import Categories
from bas_air_unit_network_dataset.models.waypoint import Waypoint


class WaypointCollection:
    """
    A collection of Waypoints.

    Provides a dictionary like interface to managing Waypoints, along with methods for managing multiple Waypoints at
    once.
    """

    def __init__(self) -> None:
        """Create routes collection."""
        self._waypoints: list[Waypoint] = []

    @property
    def waypoints(self) -> list[Waypoint]:
        """Get all waypoints in collection as Waypoint classes."""
        return self._waypoints

    @property
    def report_waypoints(self) -> list[WaypointsReportWaypoint]:
        """Get all waypoints in collection structured for use in reports."""
        return [waypoint.dumps_report() for waypoint in self.waypoints]

    @property
    def categories(self) -> Categories:
        """Get category objects for waypoints in collection."""
        categories = [waypoint.category for waypoint in self.waypoints]
        return Categories(categories)

    def _report_waypoints_in_category(self, category: str) -> list[WaypointsReportWaypoint]:
        return [waypoint for waypoint in self.report_waypoints if waypoint.category == category]

    def append(self, waypoint: Waypoint) -> None:
        """
        Add waypoint to collection.

        For consistency waypoints are sorted by identifier.
        """
        self._waypoints.append(waypoint)
        self._waypoints = sorted(self.waypoints, key=lambda x: x.identifier)

    def lookup(self, identifier: str) -> Optional[Waypoint]:
        """
        Get waypoint in collection specified by waypoint identifier.

        Returns `None` if no matching waypoint found.

        :param identifier: waypoint identifier
        """
        for waypoint in self._waypoints:
            if waypoint.identifier == identifier:
                return waypoint

        return None

    def loads_gpx(self, gpx_waypoints: list[GPXWaypoint]) -> None:
        """
        Read waypoints from GPX data.

        :param gpx_waypoints list of GPX waypoints
        """
        for gpx_waypoint in gpx_waypoints:
            waypoint = Waypoint()
            waypoint.loads_gpx(gpx_waypoint=gpx_waypoint)

            self.append(waypoint)

    def dump_features(self, inc_spatial: bool = True) -> list[dict]:
        """
        Build all waypoints in collection as generic features for further processing.

        This method is a wrapper around the `dumps_feature()` method for each waypoint.

        :param inc_spatial: whether to include the geometry of each waypoint in generated features
        """
        features = []

        for waypoint in self.waypoints:
            features.append(waypoint.dumps_feature(inc_spatial=inc_spatial))

        return features

    def dump_csv(self, path: Path, inc_dd_lat_lon: bool = False, inc_ddm_lat_lon: bool = False) -> None:
        """
        Write waypoints as a CSV file for further processing and/or visualisation.

        :param path: Output path
        :param inc_dd_lat_lon: include latitude and longitude columns in decimal degree format
        :param inc_ddm_lat_lon: include latitude and longitude columns in degrees decimal minutes format
        """
        fieldnames: list[str] = list(Waypoint.csv_schema.keys())
        if inc_dd_lat_lon:
            fieldnames = [
                "identifier",
                "name",
                "colocated_with",
                "latitude_dd",
                "longitude_dd",
                "last_accessed_at",
                "last_accessed_by",
                "fuel",
                "elevation_ft",
                "comment",
                "category",
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
                "fuel",
                "elevation_ft",
                "comment",
                "category",
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
                "fuel",
                "elevation_ft",
                "comment",
                "category",
            ]

        # newline parameter needed to avoid extra blank lines in files on Windows [#63]
        with path.open(mode="w", newline="", encoding="utf-8-sig") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()

            for waypoint in self.waypoints:
                writer.writerow(waypoint.dumps_csv(inc_dd_lat_lon=inc_dd_lat_lon, inc_ddm_lat_lon=inc_ddm_lat_lon))

    def dumps_gpx(self) -> GPX:
        """Build a GPX document for all waypoints within collection."""
        gpx = GPX()

        for waypoint in self.waypoints:
            gpx.waypoints.append(waypoint.dumps_gpx())

        return gpx

    def dump_gpx(self, path: Path) -> None:
        """Write waypoints as a GPX file for use in GPS devices."""
        with path.open(mode="w") as gpx_file:
            gpx_file.write(self.dumps_gpx().to_xml())

    def dumps_fpl(self) -> Fpl:
        """Build a FPL document for all waypoints within collection."""
        fpl = Fpl()

        for waypoint in self.waypoints:
            fpl.waypoints.append(waypoint.dumps_fpl())

        fpl.validate()

        return fpl

    def dump_fpl(self, path: Path) -> None:
        """Write waypoints as a FPL file for use in aircraft GPS devices."""
        fpl = self.dumps_fpl()
        fpl.dump_xml(path=path)

    def dumps_report_html(self, template_path: Path, title: str) -> str:
        """Build an HTML report for waypoints."""
        if not template_path.exists():
            msg = f"Error: template not found: {template_path.absolute()}"
            raise FileNotFoundError(msg)

        jinja = Environment(loader=FileSystemLoader(template_path.parent), autoescape=True)
        template = jinja.get_template(template_path.name)

        categories = self.categories
        item_categories = []
        for category in categories.as_list:
            item_categories.append({"category": category, "rows": self._report_waypoints_in_category(category.name)})

        meta = {
            "title": title,
            "time": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"),
            "template": template_path.name,
            "category_colours": categories.colours,
        }

        return template.render(items=self.report_waypoints, item_categories=item_categories, meta=meta)

    def dump_report_html(self, template_path: Path, title: str, path: Path) -> None:
        """Write waypoints report as an HTML file."""
        html = self.dumps_report_html(template_path=template_path, title=title)
        with path.open(mode="w") as file:
            file.write(html)

    def dump_report_pdf(self, template_path: Path, title: str, path: Path) -> None:
        """Write waypoints report as a PDF file."""
        pdf = HTML(string=self.dumps_report_html(template_path=template_path, title=title))
        with path.open(mode="wb") as file:
            pdf.write_pdf(file)

    def __getitem__(self, _id: str) -> Waypoint:
        """
        Get a waypoint by its ID.

        :param _id: a waypoint ID (distinct from a waypoint's Identifier)
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
        """Waypoints in WaypointCollection."""
        return len(self.waypoints)

    def __repr__(self) -> str:
        """Representation of WaypointCollection as a string."""
        return f"<WaypointCollection : {self.__len__()} waypoints>"
