from datetime import datetime
from typing import List, Dict, Union


def _convert_coordinate_dd_2_ddm(coordinate: float, positive_symbol: str, negative_symbol: str) -> Dict[str, float]:
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
        "lon": f"{int(lon['degree'])}° {'{:.6f}'.format(lon['minutes'])}' {lon['sign']}",
        "lat": f"{int(lat['degree'])}° {'{:.6f}'.format(lat['minutes'])}' {lat['sign']}",
    }


def file_name_with_date(name: str) -> str:
    return name.replace("{{date}}", f"{datetime.utcnow().date().strftime('%Y_%m_%d')}")
