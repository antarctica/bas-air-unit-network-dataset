from __future__ import annotations

from contextlib import suppress
from datetime import datetime, timezone
from typing import Union


def _convert_coordinate_dd_2_ddm(coordinate: float, positive_symbol: str, negative_symbol: str) -> dict[str, float]:
    """
    Convert a coordinate axis from decimal degrees (DD) to degrees decimal minutes (DDM).

    The maths and logic used for this conversion is taken from the US Polar Geospatial Centre (PGC) coordinate
    converter - https://github.com/PolarGeospatialCenter/pgc-coordinate-converter,

    For example, a coordinate value of '-69.91516669280827' with positive symbol 'N' and negative 'S', becomes:
    `{'degree': 69.0, 'minutes': 54.9100015684962, 'sign': 'S'}`.

    :type coordinate: float
    :param coordinate: Coordinate axis value to convert
    :type positive_symbol: str
    :param positive_symbol: Symbol to use if converted value is positive
    :type negative_symbol; str
    :param negative_symbol: Symbol to use if converted value is negative
    :rtype: dict
    :return: Converted coordinate split into degrees, minutes and positive/negative symbol
    """
    coordinate_elements: list[str] = str(coordinate).split(".")

    ddm_coordinate: dict[str, Union[float, str]] = {
        "degree": abs(float(coordinate_elements[0])),
        "minutes": 0,
        "sign": negative_symbol,
    }

    with suppress(IndexError):
        ddm_coordinate["minutes"] = abs(float(f"0.{coordinate_elements[1]}") * 60.0)

    if coordinate >= 0:
        ddm_coordinate["sign"] = positive_symbol

    return ddm_coordinate


def convert_coordinate_dd_2_ddm(lon: float, lat: float) -> dict[str, str]:
    """
    Convert coordinate from decimal degrees (DD) to degrees decimal minutes (DDM).

    The DDM representation is used by pilots and is an output only format. Minutes are rounded to 6 decimal places.

    For example, a coordinate of '-50.846166657283902, -69.91516669280827' (lon, lat) becomes:
    `{'lon': "50° 50.769999' W", 'lat': "69° 54.910002' S"}`.

    :type lon: float
    :param lon: longitude
    :type lat: float
    :param lat: latitude
    :return:
    """
    lon = _convert_coordinate_dd_2_ddm(lon, positive_symbol="E", negative_symbol="W")
    lat = _convert_coordinate_dd_2_ddm(lat, positive_symbol="N", negative_symbol="S")

    return {
        "lon": f"{int(lon['degree'])}° {'{:.6f}'.format(lon['minutes'])}' {lon['sign']}",
        "lat": f"{int(lat['degree'])}° {'{:.6f}'.format(lat['minutes'])}' {lat['sign']}",
    }


def file_name_with_date(name: str) -> str:
    """
    Generate file name string with placeholder replaced by current date.

    This function is intended for use in generating date stamped file names. The date value is formatted as an ISO 8601
    date (i.e. 'YYYY-MM-DD'). The input file name must contain the placeholder '{{date}}' to be correctly substituted.

    For example if today's date is May 24th 2014, an input of: 'foo-{{date}}' is returned as 'foo-2014-05-24'.

    :type name: str
    :param name: file name containing date placeholder
    :rtype str
    :return: file name containing current date
    """
    return name.replace("{{date}}", f"{datetime.now(tz=timezone.utc).date().strftime('%Y_%m_%d')}")
