from datetime import datetime
from typing import Dict, List, Union


def _convert_coordinate_dd_2_ddm(coordinate: float, positive_symbol: str, negative_symbol: str) -> Dict[str, float]:
    """
    Converts a coordinate axis from decimal degrees (DD) to degrees decimal minutes (DDM).

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
    coordinate_elements: List[str] = str(coordinate).split(".")

    ddm_coordinate: Dict[str, Union[float, str]] = {
        "degree": abs(float(coordinate_elements[0])),
        "minutes": 0,
        "sign": negative_symbol,
    }

    try:
        ddm_coordinate["minutes"] = abs(float(f"0.{coordinate_elements[1]}") * 60.0)
    except IndexError:
        pass

    if coordinate >= 0:
        ddm_coordinate["sign"] = positive_symbol

    return ddm_coordinate


def convert_coordinate_dd_2_ddm(lon: float, lat: float) -> Dict[str, str]:
    lon = _convert_coordinate_dd_2_ddm(lon, positive_symbol="E", negative_symbol="W")
    lat = _convert_coordinate_dd_2_ddm(lat, positive_symbol="N", negative_symbol="S")

    return {
        "lon": f"{int(lon['degree'])}° {'{:.6f}'.format(lon['minutes'])} {'{:.6f}'.format(lon['minutes'])}' {lon['sign']}",
        "lat": f"{int(lat['degree'])}° {'{:.6f}'.format(lat['minutes'])}' {lat['sign']}",
    }


def file_name_with_date(name: str) -> str:
    return name.replace("{{date}}", f"{datetime.utcnow().date().strftime('%Y_%m_%d')}")
