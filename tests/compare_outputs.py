from datetime import UTC, date, datetime
from hashlib import sha256
from pathlib import Path


def _sha256sum(path: Path) -> str:
    """Calculate checksum for file."""
    file_hash = sha256()
    with path.open("rb") as file:
        while True:
            chunk = file.read(file_hash.block_size)
            if not chunk:
                break
            file_hash.update(chunk)
    return file_hash.hexdigest()


def _make_paths(base_path: Path, date_: date) -> list[Path]:
    """
    Create list of expected file paths for instance of test network.

    As the contents of the test network is known and controlled.

    A fixed date is required as some output file names include the current date.
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
        base_path.joinpath(f"./PDF/00_WAYPOINTS_{date_str}.pdf"),
    ]


def _check_for_unexpected_paths(expected_paths: list[Path], search_path: Path) -> None:
    """
    Check whether a directory contains files other than a list of expected values.

    If an unexpected file is found, and is not ignored, a RuntimeError will be raised for the unexpected file.
    """
    ignored_files = [".DS_Store"]
    for path in search_path.glob("**/*.*"):
        if path not in expected_paths and path.name not in ignored_files:
            print(expected_paths)
            msg = f"Unexpected path {path.resolve()!r} found - aborting."
            raise RuntimeError(msg)


def _compare_outputs_with_reference(reference_paths: list[Path], comparison_paths: list[Path]) -> None:
    """
    Check the contents of a list of reference and candidate files are the same.

    File paths in reference and candidate lists must be in the same order. Files are compared by checksum. Non-matching
    hashes will raise a RuntimeError.

    Skips PDF reports.
    """
    for x, y in zip(reference_paths, comparison_paths, strict=True):
        if y.suffix == ".pdf":
            continue

        x_sha256 = _sha256sum(path=x)
        y_sha256 = _sha256sum(path=y)
        if x_sha256 != y_sha256:
            msg = f"File {x.name!r} with SHA256 [{x_sha256}] != to {y.name!r} [{y_sha256}]."
            raise RuntimeError(msg)

    print("SHA256 checksums match reference values.")
    print("Note: PDF export hashes are not compared as they contain timestamps that cannot easily be controlled for.")


def _run(reference_path: Path, reference_date: date, output_path: Path) -> None:
    reference_paths = _make_paths(base_path=reference_path.resolve(), date_=reference_date)
    outputs_paths = _make_paths(base_path=output_path.resolve(), date_=datetime.now(tz=UTC).date())

    _check_for_unexpected_paths(expected_paths=reference_paths, search_path=reference_path.resolve())
    _check_for_unexpected_paths(expected_paths=outputs_paths, search_path=output_path.resolve())

    _compare_outputs_with_reference(reference_paths=reference_paths, comparison_paths=outputs_paths)


def main() -> None:
    """Entrypoint."""
    base_path = Path(__file__).parent
    output_path = base_path / "out"
    reference_path = base_path / "resources/test-network/reference-outputs/"
    reference_date = date(2026, 11, 23)
    print(f"{reference_path.resolve() =}")
    print(f"{output_path.resolve() =}")

    _run(reference_path=reference_path, reference_date=reference_date, output_path=output_path)


if __name__ == "__main__":
    main()
