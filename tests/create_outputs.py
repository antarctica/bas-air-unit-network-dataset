import argparse
from pathlib import Path

from bas_air_unit_network_dataset.networks.bas_air_unit import MainAirUnitNetwork


def main() -> None:
    """Program control."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_gpx")
    parser.add_argument("output_dir")
    args = parser.parse_args()

    input_path = Path(args.input_gpx)
    output_path = Path(args.output_dir)

    print(f"Input path: {input_path.resolve()}")
    print(f"Output path: {output_path.resolve()}")

    input_gpx = Path("./tests/resources/test-network/test-network.gpx")
    network = MainAirUnitNetwork(output_path=output_path)

    network.load_gpx(path=input_gpx)
    network.display()

    network.dump_csv()
    network.dump_gpx()
    network.dump_fpl()

    print("\nOutput files:")
    for path in output_path.glob("**/*"):
        print(path.resolve())


if __name__ == "__main__":
    main()
