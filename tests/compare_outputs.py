import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path

reference_path = Path("./tests/resources/test-network/reference-outputs/")
reference_date = date(2024, 11, 22)


def sha256sum(path: Path) -> str:
    """
    Calculate checksum for file using SHA256 hash.

    :type path: Path
    :param path: file to hash
    :rtype: str
    :return: SHA256 checksum
    """
    file_hash = sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(file_hash.block_size)
            if not chunk:
                break
            file_hash.update(chunk)

    return file_hash.hexdigest()


def make_paths(base_path: Path, date_: date) -> list[Path]:
    """
    Create list of expected file paths for instance of test network.

    As the contents of the test network is known and controlled.

    A date is required as some output file names include the current date.

    :type base_path: path
    :param base_path: directory containing instance of test network
    :type date_: date
    :param date_:
    :rtype list
    :return: paths that should exist
    """
    date_str = date_.isoformat().replace("-", "_")

    return [
        base_path.joinpath(f"./CSV/00_WAYPOINTS_DDM_{date_str}.csv"),
        base_path.joinpath(f"./CSV/00_WAYPOINTS_DD_{date_str}.csv"),
        base_path.joinpath(f"./FPL/00_WAYPOINTS_{date_str}.fpl"),
        base_path.joinpath("./FPL/01_BRAVO_TO_ALPHA.fpl"),
        base_path.joinpath("./FPL/02_BRAVO_TO_BRAVO.fpl"),
        base_path.joinpath("./FPL/03_BRAVO_TO_LIMA.fpl"),
        base_path.joinpath(f"./GPX/00_NETWORK_{date_str}.gpx"),
    ]


def check_for_unexpected_paths(expected_paths: list[Path], search_path: Path) -> None:
    """
    Check whether a directory contains files other than a list of expected values.

    If an unexpected file is found, the file name is checked against a list of ignored values (system files etc.).
    If not ignored, a RuntimeError will be raised for the unexpected file.

    :type expected_paths: list
    :param expected_paths: paths that are expected in directory
    :type search_path: Path
    :param search_path: directory to check
    :raises RuntimeError: unexpected path found
    """
    ignored_files = [".DS_Store"]

    for path in search_path.glob("**/*.*"):
        if path not in expected_paths and path.name not in ignored_files:
            print(expected_paths)
            msg = f"Unexpected path {path.resolve()!r} found - aborting."
            raise RuntimeError(msg)


def compare_outputs_with_reference(reference_paths: list[Path], comparison_paths: list[Path]) -> None:
    """
    Check the contents of a list of reference and comparison files are the same.

    File paths in reference and comparison lists must be in the same order. Files are compared by comparing a SHA256
    hash of each file. Non-matching hashes will raise a RuntimeError.

    :param reference_paths:
    :param comparison_paths:
    :raises RuntimeError: comparison file checksum does not match reference file
    """
    for x, y in zip(reference_paths, comparison_paths):
        x_sha256 = sha256sum(path=x)
        y_sha256 = sha256sum(path=y)

        if x_sha256 != y_sha256:
            msg = f"File {x.name !r} with SHA256 [{x_sha256}] != to {y.name !r} [{y_sha256}]."
            raise RuntimeError(msg)

    print("SHA256 checksums match reference values.")


def main() -> None:
    """Program control."""
    parser = argparse.ArgumentParser()
    parser.add_argument("outputs")
    args = parser.parse_args()
    outputs_path = Path(args.outputs)

    print(f"{reference_path.resolve() =}")
    print(f"{outputs_path.resolve() =}")

    reference_paths = make_paths(base_path=reference_path.resolve(), date_=reference_date)
    outputs_paths = make_paths(base_path=outputs_path.resolve(), date_=datetime.now(tz=timezone.utc).date())

    check_for_unexpected_paths(expected_paths=reference_paths, search_path=reference_path.resolve())
    check_for_unexpected_paths(expected_paths=outputs_paths, search_path=outputs_path.resolve())

    compare_outputs_with_reference(reference_paths=reference_paths, comparison_paths=outputs_paths)


if __name__ == "__main__":
    main()
