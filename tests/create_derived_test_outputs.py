import json
from pathlib import Path


def load_test_network(path: Path) -> dict:
    """
    Load network features from JSON file.

    :type path: Path
    :param path: location of JSON file.
    :rtype dict
    :return feature data
    """
    with open(path, mode="r") as network_file:
        return json.load(network_file)


def convert_to_geojson(network: str, data: dict, path: Path) -> None:
    """
    Convert network features to GeoJSON.

    So they can be visualised in GIS tools as the canonical format for test networks is not a standard format.

    :param network: name of test network
    :type data: dict
    :param data: network features
    :type path: Path
    :param path: where to create output file
    """
    features = {"type": "FeatureCollection", "name": network, "features": []}

    for waypoint in data["waypoints"]:
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [waypoint["lon"], waypoint["lat"]]},
            "properties": {
                "feature_type": "waypoint",
                "identifier": waypoint["callsign"],
                "name": waypoint["name"],
                "comment": waypoint["comment"],
                "last_accessed_at": waypoint["last_accessed_at"],
                "last_accessed_by": waypoint["last_accessed_by"],
            },
        }
        for property_ in ["name", "last_accessed_at", "last_accessed_by", "comment"]:
            if waypoint[property_] is not None:
                feature["properties"][property_] = waypoint[property_]
        features["features"].append(feature)

    for route in data["routes"]:
        feature = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": []},
            "properties": {"feature_type": "route", "name": route["name"]},
        }
        for waypoint_id in route["waypoints"]:
            for waypoint in data["waypoints"]:
                if waypoint["callsign"] == waypoint_id["waypoint_designator"]:
                    feature["geometry"]["coordinates"].append([waypoint["lon"], waypoint["lat"]])
                    break

        features["features"].append(feature)

    with open(path, mode="w") as file:
        json.dump(features, file, indent=True, sort_keys=True)


def main() -> None:
    """Program control."""
    network_name = "test-network"
    base_path = Path(f"tests/resources/{network_name}")

    input_path = base_path.joinpath(f"{network_name}.json")
    geojson_path = base_path.joinpath(f"{network_name}.geojson")

    features = load_test_network(path=input_path)
    print("features loaded")
    convert_to_geojson(network=network_name, data=features, path=geojson_path)
    print("features converted to GeoJSON")


if __name__ == "__main__":
    main()
    print("Script exited normally")
