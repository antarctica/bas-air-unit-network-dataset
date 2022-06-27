import json
from pathlib import Path
from typing import List

from bas_air_unit_waypoints import (
    Waypoint,
    Route,
    WaypointCollection,
    NetworkManager,
)


class TestNetworkManager(NetworkManager):
    def __init__(self, data_path: Path):
        super().__init__()
        self.data_path: Path = data_path
        self.load_test_data()

    def load_test_data(self) -> None:
        with open(self.data_path, mode="r") as test_data_file:
            raw_test_data: dict = json.load(test_data_file)

        self.load_test_waypoints(raw_waypoints=raw_test_data["waypoints"])
        self.load_test_routes(raw_routes=raw_test_data["routes"], waypoints=self.waypoints)

    def load_test_waypoints(self, raw_waypoints: List[dict]) -> None:
        for raw_waypoint in raw_waypoints:
            self.waypoints.append(
                Waypoint(
                    designator=raw_waypoint["callsign"],
                    lon=raw_waypoint["lon"],
                    lat=raw_waypoint["lat"],
                    comment=raw_waypoint["comment"],
                )
            )

    def load_test_routes(self, raw_routes: List[dict], waypoints: WaypointCollection):
        for raw_route in raw_routes:
            self.routes.append(
                Route(
                    name=raw_route["name"],
                    route_waypoints=raw_route["waypoints"],
                    waypoints=waypoints,
                )
            )

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


if __name__ == "__main__":
    test_network = TestNetworkManager(data_path=test_data_path)
    print(test_network)
    print("")
    test_network.describe()
