from csv import DictWriter
from dataclasses import fields
from datetime import date
from pathlib import Path

from gpxpy.gpx import GPX

from bas_air_unit_network_dataset.exporters.fpl.fpl import Fpl
from bas_air_unit_network_dataset.exporters.html.html import WaypointsReport
from bas_air_unit_network_dataset.exporters.pdf.pdf import PdfReport
from bas_air_unit_network_dataset.models.base.network import Network
from bas_air_unit_network_dataset.models.base.route import Route
from bas_air_unit_network_dataset.models.base.waypoint import Waypoint
from bas_air_unit_network_dataset.models.formats.csv import Waypoint as CsvWaypoint
from bas_air_unit_network_dataset.models.formats.fpl import Route as FplRoute
from bas_air_unit_network_dataset.models.formats.fpl import Waypoint as FplWaypoint
from bas_air_unit_network_dataset.models.formats.gpx import Route as GpxRoute
from bas_air_unit_network_dataset.models.formats.gpx import Waypoint as GpxWaypoint
from bas_air_unit_network_dataset.models.formats.html import WaypointsReportWaypoint


class BasAirUnitMainNetwork(Network):
    """
    BAS Air Unit main travel network.

    Extends Network class to use BAS Air Unit naming conventions and create outputs.

    The `updated_at` argument should represent when source data was last updated, not the current time.
    """

    def __init__(self, update_at: date, output_path: Path, waypoints: list[Waypoint], routes: list[Route]) -> None:
        super().__init__(waypoints=waypoints, routes=routes)
        self._output_path = output_path
        self._revision_date = update_at
        self._revision_date_fmt = self._revision_date.strftime("%Y_%m_%d")

    def dump_waypoints_csv(self) -> None:
        """
        Write network waypoints as CSV files for further processing and/or visualisation.

        Waypoints are written using decimal degrees (DD) to suit BAS Field Operations and decimal degrees minutes (DDM)
        to suit the BAS Air Unit.

        Explicit newline parameter needed to avoid extra blank lines in files on Windows [#63].

        Files are named according to Air Unit conventions.
        """
        base_path = self._output_path.joinpath("CSV")
        base_path.mkdir(parents=True, exist_ok=True)

        headings = [field.name for field in fields(Waypoint) if field.name not in {"id", "lon", "lat"}]
        # insert dd/ddm column names at the relevant place
        coordinate_heading_index = headings.index("colocated_with") + 1
        ddm_headings = (
            headings[:coordinate_heading_index]
            + ["latitude_ddm", "longitude_ddm"]
            + headings[coordinate_heading_index:]
        )
        dd_headings = (
            headings[:coordinate_heading_index] + ["latitude_dd", "longitude_dd"] + headings[coordinate_heading_index:]
        )

        csv_waypoints = [CsvWaypoint.loads(wp) for wp in self._waypoints]

        ddm_path = f"00_WAYPOINTS_DDM_{self._revision_date_fmt}.csv"
        with base_path.joinpath(ddm_path).open("w", newline="", encoding="utf-8-sig") as f:
            writer = DictWriter(f, fieldnames=ddm_headings)
            writer.writeheader()
            writer.writerows([wp.dumps(inc_ddm_lat_lon=True) for wp in csv_waypoints])

        dd_path = f"00_WAYPOINTS_DD_{self._revision_date_fmt}.csv"
        with base_path.joinpath(dd_path).open("w", newline="", encoding="utf-8-sig") as f:
            writer = DictWriter(f, fieldnames=dd_headings)
            writer.writeheader()
            writer.writerows([wp.dumps(inc_dd_lat_lon=True) for wp in csv_waypoints])

    def dump_network_gpx(self) -> None:
        """
        Write network wide GPX file for use in GPS devices.

        Contains all routes and waypoints.

        File is named according to Air Unit conventions.
        """
        path = self._output_path.joinpath("GPX") / f"00_NETWORK_{self._revision_date_fmt}.gpx"
        path.parent.mkdir(parents=True, exist_ok=True)

        gpx = GPX()
        gpx.waypoints = [GpxWaypoint.loads(wp).dumps() for wp in self._waypoints]
        gpx.routes = [GpxRoute.loads(r).dumps() for r in self._routes]

        with path.open(mode="w") as f:
            f.write(gpx.to_xml())
            pass

    def dump_waypoints_fpl(self) -> None:
        """
        Write waypoints as a Garmin FPL file for use in aircraft GPS devices.

        File is named according to Air Unit conventions.
        """
        path = self._output_path.joinpath("FPL") / f"00_WAYPOINTS_{self._revision_date_fmt}.fpl"
        path.parent.mkdir(parents=True, exist_ok=True)

        fpl = Fpl(waypoints=[FplWaypoint.loads(wp) for wp in self._waypoints])
        fpl.validate()

        with path.open(mode="w") as f:
            f.write(fpl.dumps().decode())

    def dump_routes_fpl(self) -> None:
        """
        Write routes as Garmin FPL files for use in aircraft GPS devices.

        Routes are written as separate files as FPL doesn't support combined routes.

        Route in this network are assumed to be exclusive, with each route assigned a flight plan index corresponding
        to its list order (rather than any fixed value), starting from `1`.

        Networks exceeding the supported route count are rejected before creating any output files.

        Files are named according to Air Unit conventions. The Air Unit uses underscores as separators in route names,
        which aren't allowed, so we convert these to spaces (which are).
        """
        max_routes = FplRoute._max_index_count
        if len(self._routes) > max_routes:
            msg = f"Cannot export more than {max_routes} FPL routes; network contains {len(self._routes)}."
            raise ValueError(msg)

        base_path = self._output_path.joinpath("FPL")
        base_path.mkdir(parents=True, exist_ok=True)

        flight_plan_index = 1
        for route in self._routes:
            fpl = Fpl(route=FplRoute.loads(route=route, index=flight_plan_index))
            fpl.validate()

            file_name = f"{str(flight_plan_index).zfill(2)}_{route.first_waypoint.waypoint.identifier.upper()}_TO_{route.last_waypoint.waypoint.identifier.upper()}.fpl"
            with base_path.joinpath(file_name).open(mode="w") as f:
                f.write(fpl.dumps().decode())

            flight_plan_index += 1

    def dump_waypoints_report_pdf(self) -> None:
        """
        Write waypoints as a formatted PDF report for reference and printing.

        Waypoints are written using decimal degrees minutes (DDM) and YYYY-MMM-DD dates to suit the BAS Air Unit.

        File is named according to Air Unit conventions.
        """
        path = self._output_path.joinpath("PDF") / f"00_WAYPOINTS_{self._revision_date_fmt}.pdf"
        path.parent.mkdir(parents=True, exist_ok=True)

        report = WaypointsReport(
            waypoints=[WaypointsReportWaypoint.loads(wp) for wp in self._waypoints],
            revision_date=self._revision_date,
        )
        output = PdfReport(content=report.dumps())
        output.dump(path)
