from __future__ import annotations

from datetime import UTC, datetime


def _convert_coordinate_dd_2_ddm(
    coordinate: float, positive_symbol: str, negative_symbol: str, *, decimal_places: int = 6
) -> tuple[int, float, str]:
    """
    Convert a coordinate axis from decimal degrees (DD) to degrees decimal minutes (DDM).

    Minutes are rounded to the requested precision, carrying into degrees when they round to 60.

    For example, a coordinate value of '-69.91516669280827' with positive symbol 'N' and negative 'S' returns:
    `(69, 54.910002, 'S')`.
    """
    absolute_coordinate = abs(coordinate)
    degree = int(absolute_coordinate)
    minutes = round((absolute_coordinate - degree) * 60.0, decimal_places)
    if minutes >= 60:  # noqa: PLR2004
        degree += 1
        minutes = 0.0
    sign = positive_symbol if coordinate >= 0 else negative_symbol

    return degree, minutes, sign


def convert_coordinate_dd_2_ddm(lon: float, lat: float) -> tuple[str, str]:
    """
    Convert coordinate from decimal degrees (DD) to degrees decimal minutes (DDM).

    The DDM representation is used by pilots and is an output only format. Minutes are rounded to 6 decimal places.

    For example, a coordinate of '-50.846166657283902, -69.91516669280827' (lon, lat) returns:
    `("50° 50.769999' W", "69° 54.910002' S")` (longitude, latitude).
    """
    lon_degree, lon_minutes, lon_sign = _convert_coordinate_dd_2_ddm(lon, positive_symbol="E", negative_symbol="W")
    lat_degree, lat_minutes, lat_sign = _convert_coordinate_dd_2_ddm(lat, positive_symbol="N", negative_symbol="S")

    return (
        f"{int(lon_degree)}° {f'{lon_minutes:.6f}'}' {lon_sign}",
        f"{int(lat_degree)}° {f'{lat_minutes:.6f}'}' {lat_sign}",
    )


def convert_coordinate_dd_2_ddm_padded(lon: float, lat: float) -> tuple[str, str]:
    """
    Convert coordinate from decimal degrees (DD) to degrees decimal minutes (DDM) with padding and rounding.

    In this format values use fixed padding for easier reading in tabular form.
    Minutes are rounded to 3 decimal places and displayed with 6 decimal places.

    For example, a coordinate of '-50.846166657283902, -69.91516669280827' (lon, lat) becomes:
    `("050° 50.770000' W", "69° 54.910000' S")`.
    """
    lon_degree, lon_minutes, lon_sign = _convert_coordinate_dd_2_ddm(
        lon, positive_symbol="E", negative_symbol="W", decimal_places=3
    )
    lat_degree, lat_minutes, lat_sign = _convert_coordinate_dd_2_ddm(
        lat, positive_symbol="N", negative_symbol="S", decimal_places=3
    )

    return (
        f"{str(int(lon_degree)).zfill(3)}° {f'{lon_minutes:.6f}'.zfill(9)}' {lon_sign}",
        f"{str(int(lat_degree)).zfill(2)}° {f'{lat_minutes:.6f}'.zfill(9)}' {lat_sign}",
    )


def file_name_with_date(name: str) -> str:
    """
    Generate file name string with placeholder replaced by current date.

    This function is intended for use in generating date stamped file names. The date value is formatted as
    'YYYY_MM_DD'. The input file name must contain the placeholder '{{date}}' to be correctly substituted.

    For example if today's date is May 24th 2014, an input of: 'foo-{{date}}' is returned as 'foo-2014_05_24'.
    """
    return name.replace("{{date}}", f"{datetime.now(tz=UTC).date().strftime('%Y_%m_%d')}")
