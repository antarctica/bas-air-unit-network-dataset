import json
from pathlib import Path
from typing import List

from bas_air_unit_waypoints import (
    Waypoint,
    Route,
    WaypointCollection,
    NetworkManager,
    RouteWaypoint,
)


class TestNetworkManager(NetworkManager):
    def __init__(self, data_path: Path):
        super().__init__()
        self.data_path: Path = data_path

    def load_test_data(self) -> None:
        with open(self.data_path, mode="r") as test_data_file:
            raw_test_data: dict = json.load(test_data_file)

        self._load_test_waypoints(raw_waypoints=raw_test_data["waypoints"])
        self._load_test_routes(raw_routes=raw_test_data["routes"], waypoints=self.waypoints)

    def _load_test_waypoints(self, raw_waypoints: List[dict]) -> None:
        for raw_waypoint in raw_waypoints:
            self.waypoints.append(
                Waypoint(
                    designator=raw_waypoint["callsign"],
                    lon=raw_waypoint["lon"],
                    lat=raw_waypoint["lat"],
                    comment=raw_waypoint["comment"],
                    last_accessed_at=raw_waypoint["last_accessed_at"],
                    last_accessed_by=raw_waypoint["last_accessed_by"],
                )
            )

    def _load_test_routes(self, raw_routes: List[dict], waypoints: WaypointCollection):
        for raw_route in raw_routes:
            route = Route(name=raw_route["name"])
            waypoints: List[RouteWaypoint] = []

            sequence = 1
            for waypoint in raw_route["waypoints"]:
                route_waypoint = RouteWaypoint()

                # find waypoint by designator
                for _waypoint in self.waypoints:
                    if _waypoint.designator == waypoint["waypoint_designator"]:
                        route_waypoint.waypoint = _waypoint
                if route_waypoint.waypoint is None:
                    raise RuntimeError(
                        f"Unable to find Waypoint with designator '[{waypoint['waypoint_designator']}]' in Waypoints list."
                    )

                route_waypoint.sequence = sequence

                if "description" in waypoint:
                    route_waypoint.description = waypoint["description"]

                waypoints.append(route_waypoint)
                sequence += 1

            route.waypoints = waypoints

            self.routes.append(route)

    def describe(self) -> None:
        print(f"Waypoints in test WaypointCollection [{len(self.waypoints)}]:")
        for i, test_waypoint in enumerate(self.waypoints):
            print(f"{str(i + 1).zfill(2)}. {test_waypoint}")
        print("")
        print(f"Routes in test RouteCollection [{len(self.routes)}]:")
        for i, test_route in enumerate(self.routes):
            print(f"{str(i + 1).zfill(2)}. {test_route}")

    def __repr__(self):
        return f"<TestNetworkManager : {len(self.waypoints)} Waypoints - {len(self.routes)} Routes>"


test_data_path = Path("test-data-raw.json")
test_dataset_path = Path("test-dataset.gpkg")
test_output_path = Path("output")


def populate_test_network(network: TestNetworkManager, gpkg_path: Path):
    gpkg_path.unlink(missing_ok=True)
    network.load_test_data()
    print(network)
    print("")
    network.describe()
    network.dump_gpkg(path=gpkg_path)


def generate_outputs(network: TestNetworkManager, gpkg_path: Path, output_path: Path):
    network.load_gpkg(path=gpkg_path)
    print(network)
    print("")
    network.describe()
    print("")
    network.dump_csv(path=output_path)
    print("CSV export complete")
    network.dump_gpx(path=output_path)
    print("GPX export complete")
    network.dump_fpl(path=output_path)
    print("FPL export complete")


if __name__ == "__main__":
    test_network = TestNetworkManager(data_path=test_data_path)

    # # uncomment to setup GeoPackage from test data
    # populate_test_network(network=test_network, gpkg_path=test_dataset_path)

    # # uncomment to generate CSV/GPX/etc. outputs from test data
    generate_outputs(network=test_network, gpkg_path=test_dataset_path, output_path=test_output_path)
