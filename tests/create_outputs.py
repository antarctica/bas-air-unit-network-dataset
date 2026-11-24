from datetime import UTC, datetime
from pathlib import Path

import geojson
from geojson import FeatureCollection

from bas_air_unit_network_dataset.models.base.route import Route
from bas_air_unit_network_dataset.models.base.waypoint import Waypoint
from bas_air_unit_network_dataset.networks.bas_air_unit_main import BasAirUnitMainNetwork


def _split_geojson(source: Path) -> tuple[FeatureCollection, FeatureCollection]:
    """Divide test network feature collection into routes and waypoints."""
    waypoints = FeatureCollection(features=[])
    routes = FeatureCollection(features=[])
    with source.open() as f:
        fc = geojson.load(f)
        for feat in fc.features:
            if feat.properties["feature_type"] == "waypoint":
                waypoints.features.append(feat)
            elif feat.properties["feature_type"] == "route":
                routes.features.append(feat)
    return waypoints, routes


def _run(input_path: Path, output_path: Path) -> None:
    """Create outputs."""
    updated_at = datetime.now(tz=UTC).date()
    waypoint_features, route_features = _split_geojson(input_path)

    waypoints = [Waypoint.loads_feature(wp) for wp in waypoint_features.features]
    routes = [Route.loads_feature(feature=r, reference_waypoints=waypoints) for r in route_features.features]
    network = BasAirUnitMainNetwork(update_at=updated_at, output_path=output_path, waypoints=waypoints, routes=routes)
    print(network.display())

    network.dump_waypoints_csv()
    network.dump_network_gpx()
    network.dump_waypoints_fpl()
    network.dump_routes_fpl()
    network.dump_waypoints_report_pdf()


def main() -> None:
    """Entrypoint."""
    base_path = Path(__file__).parent
    input_path = base_path / "resources" / "test-network" / "test-network.geojson"
    output_path = base_path / "out"
    print(f"{input_path.resolve() =}")
    print(f"{output_path.resolve() =}")

    _run(input_path=input_path, output_path=output_path)
    print("\nOutput files:")
    for path in output_path.glob("**/*"):
        print(path.resolve())


if __name__ == "__main__":
    main()
