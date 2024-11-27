from __future__ import annotations

from copy import copy
from pathlib import Path
from typing import Optional

from importlib_resources import as_file as resources_as_file
from importlib_resources import files as resources_files

from bas_air_unit_network_dataset.models.network import Network
from bas_air_unit_network_dataset.models.routes import RouteCollection
from bas_air_unit_network_dataset.models.waypoints import WaypointCollection
from bas_air_unit_network_dataset.utils import file_name_with_date


class MainAirUnitNetwork(Network):
    """
    BAS Air Unit main travel network.

    Extends Network class to use BAS Air Unit naming conventions and create custom outputs.
    """

    def __init__(
        self,
        output_path: Path,
        waypoints: Optional[WaypointCollection] = None,
        routes: Optional[RouteCollection] = None,
    ) -> None:
        super().__init__(waypoints=waypoints, routes=routes)
        self._output_path = output_path

    def dump_csv(self) -> None:
        """
        Write waypoints as CSV files for further processing and/or visualisation.

        Waypoints are written using decimal degrees (DD) and decimal degrees minutes (DDM) to suit BAS Field Operations
        and the BAS Air Unit respectively.

        Files are named according to Air Unit conventions.
        """
        base_path = self._output_path.joinpath("CSV")
        base_path.mkdir(parents=True, exist_ok=True)

        self.waypoints.dump_csv(
            path=base_path.joinpath(file_name_with_date("00_WAYPOINTS_DDM_{{date}}.csv")),
            inc_ddm_lat_lon=True,
        )
        self.waypoints.dump_csv(
            path=base_path.joinpath(file_name_with_date("00_WAYPOINTS_DD_{{date}}.csv")),
            inc_dd_lat_lon=True,
        )

    def dump_gpx(self, path: Optional[Path] = None) -> None:
        """
        Write network wide GPX file for use in GPS devices.

        Contains all routes and waypoints.

        File is named according to Air Unit conventions.
        """
        path = self._output_path.joinpath(f"GPX/{file_name_with_date('00_NETWORK_{{date}}.gpx')}")
        path.parent.mkdir(parents=True, exist_ok=True)

        super().dump_gpx(path=path)

    def dump_fpl(self) -> None:
        """
        Write routes and waypoints as Garmin FPL files for use in aircraft GPS devices.

        Routes are written as separate files as FPL doesn't support combined routes.

        Route in this network are assumed to be exclusive, with each route assigned a flight plan index corresponding
        to its insert/append order, starting from `1`. I.e. the third route added to the collection has an index of `3`.

        Files are named according to Air Unit conventions. The Air Unit uses underscores as separators in route names,
        which aren't allowed, so we convert these to spaces (which are).
        """
        base_path = self._output_path.joinpath("FPL")
        base_path.mkdir(parents=True, exist_ok=True)

        waypoints_path = base_path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}.fpl"))
        self.waypoints.dump_fpl(path=waypoints_path)

        flight_plan_index = 1
        for route in self.routes:
            fpl_route = copy(route)
            fpl_route.name = fpl_route.name.replace("_", " ")
            file_name = f"{str(flight_plan_index).zfill(2)}_{route.waypoints[0].waypoint.identifier.upper()}_TO_{route.waypoints[-1].waypoint.identifier.upper()}.fpl"

            fpl_route.dump_fpl(
                path=base_path.joinpath(file_name),
                flight_plan_index=flight_plan_index,
            )
            flight_plan_index += 1

    def dump_pdf(self) -> None:
        """
        Write waypoints as a PDF formatted report files for visualisation and/or printing.

        Waypoints are written using decimal degrees minutes (DDM) and YYYY-MMM-DD dates to suit the BAS Air Unit.

        Files are named according to Air Unit conventions.
        """
        base_path = self._output_path.joinpath("PDF")
        base_path.mkdir(parents=True, exist_ok=True)

        title = "Air Unit Waypoints"
        template_name = "air_unit_waypoints.j2"
        waypoints_report_path = base_path.joinpath(file_name_with_date("00_WAYPOINTS_{{date}}.pdf"))

        with resources_as_file(resources_files("bas_air_unit_network_dataset.resources.templates")) as templates_path:
            template_path = templates_path / template_name
            self.waypoints.dump_report_pdf(template_path=template_path, title=title, path=waypoints_report_path)
