import json
from pathlib import Path

from gpxpy.gpx import GPX, GPXRoute, GPXRoutePoint, GPXWaypoint


def load_test_network(path: Path) -> dict:
    """Load network features from JSON file."""
    with path.open() as network_file:
        return json.load(network_file)


def convert_to_geojson(network: str, data: dict, path: Path) -> None:
    """
    Convert network features to GeoJSON.

    So they can be visualised in GIS tools as the canonical format for test networks is not a standard format.

    In time this method should be replaced with a TestNetworkCollection that can export to GeoJSON.

    :param network: network name
    :param data: network features
    :param path: where to create output file
    """
    features = {"type": "FeatureCollection", "name": network, "features": []}

    for waypoint in data["waypoints"]:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [waypoint["lon"], waypoint["lat"]],
            },
            "properties": {
                "feature_type": "waypoint",
                "identifier": waypoint["identifier"],
            },
        }
        for property_ in [
            "name",
            "last_accessed_at",
            "last_accessed_by",
            "colocated_with",
            "fuel",
            "elevation_ft",
            "comment",
            "category",
        ]:
            if property_ in waypoint and waypoint[property_] is not None:
                feature["properties"][property_] = waypoint[property_]
        features["features"].append(feature)

    for route in data["routes"]:
        feature = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": []},
            "properties": {"feature_type": "route", "identifier": route["identifier"]},
        }
        for route_waypoint in route["waypoints"]:
            for waypoint in data["waypoints"]:
                if waypoint["identifier"] == route_waypoint["waypoint_designator"]:
                    feature["geometry"]["coordinates"].append([waypoint["lon"], waypoint["lat"]])
                    break

        features["features"].append(feature)

    with path.open(mode="w") as file:
        json.dump(features, file, indent=True, sort_keys=True)


def convert_to_gpx(network: str, data: dict, path: Path) -> None:
    """
    Convert network features to GeoJSON.

    So a test network can be loaded as an input file.

    This method is essentially a stripped down version of the GPX export code within the main utility, with some minor
    differences to things like the description syntax, which is not ideal.
    In time this method should be replaced with a TestNetworkCollection that can load from a raw JSON input file.

    :param network: network name
    :param data: network features
    :param path: where to create output file
    """
    gpx = GPX()
    gpx.name = network

    for waypoint in data["waypoints"]:
        empty_property = "N/A"
        properties = {
            "name": empty_property,
            "colocated_with": empty_property,
            "last_accessed_at": empty_property,
            "last_accessed_by": empty_property,
            "fuel": empty_property,
            "elevation_ft": empty_property,
            "comment": empty_property,
            "category": empty_property,
        }
        for property_ in properties:
            if property_ in waypoint and waypoint[property_] is not None:
                properties[property_] = waypoint[property_]
                if isinstance(properties[property_], int):
                    properties[property_] = str(properties[property_])

        gpx_waypoint = GPXWaypoint()
        gpx_waypoint.name = waypoint["identifier"]
        gpx_waypoint.longitude = waypoint["lon"]
        gpx_waypoint.latitude = waypoint["lat"]
        gpx_waypoint.description = " | ".join(list(properties.values()))

        gpx.waypoints.append(gpx_waypoint)

    for route in data["routes"]:
        gpx_route = GPXRoute()
        gpx_route.name = route["identifier"]

        for route_waypoint in route["waypoints"]:
            for waypoint in data["waypoints"]:
                if waypoint["identifier"] == route_waypoint["waypoint_designator"]:
                    gpx_route_waypoint = GPXRoutePoint()
                    gpx_route_waypoint.name = waypoint["identifier"]
                    gpx_route_waypoint.longitude = waypoint["lon"]
                    gpx_route_waypoint.latitude = waypoint["lat"]
                    gpx_route.points.append(gpx_route_waypoint)
                    break

        gpx.routes.append(gpx_route)

    with path.open(mode="w") as gpx_file:
        gpx_file.write(gpx.to_xml())


def main() -> None:
    """Program control."""
    network_name = "test-network"
    base_path = Path(f"tests/resources/{network_name}")

    input_path = base_path.joinpath(f"{network_name}.json")
    geojson_path = base_path.joinpath(f"{network_name}.geojson")
    gpx_path = base_path.joinpath(f"{network_name}.gpx")

    features = load_test_network(path=input_path)
    print("features loaded")
    convert_to_geojson(network=network_name, data=features, path=geojson_path)
    print(f"features converted to GeoJSON - {geojson_path.resolve()}")
    convert_to_gpx(network=network_name, data=features, path=gpx_path)
    print(f"features converted to GPX - {gpx_path.resolve()}")


if __name__ == "__main__":
    main()
    print("Script exited normally")
