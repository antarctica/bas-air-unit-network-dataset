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
        print(f"Waypoints in test WaypointCollection [{self.waypoints.count}]:")
        for i, test_waypoint in enumerate(self.waypoints):
            print(f"{str(i + 1).zfill(2)}. {test_waypoint}")
        print("")
        print(f"Routes in test RouteCollection [{self.routes.count}]:")
        for i, test_route in enumerate(self.routes):
            print(f"{str(i + 1).zfill(2)}. {test_route}")

    def __repr__(self):
        return f"<TestNetworkManager : {self.waypoints.count} Waypoints - {self.routes.count} Routes>"


test_data_path = Path("test-data-raw.json")
test_dataset_path = Path("test-dataset.gpkg")
test_csv_path = Path("output")

if __name__ == "__main__":
    test_network = TestNetworkManager(data_path=test_data_path)

    # test_network.load_test_data()
    # print(test_network)
    # print("")
    # test_network.describe()
    # test_network.dump_gpkg(path=test_dataset_path)

    test_network.load_gpkg(path=test_dataset_path)
    print(test_network)
    print("")
    test_network.describe()
    test_network.dump_csv(path=test_csv_path)
