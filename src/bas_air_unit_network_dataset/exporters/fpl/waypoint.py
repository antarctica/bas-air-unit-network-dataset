from __future__ import annotations

from typing import Optional

from lxml.etree import Element, SubElement

from bas_air_unit_network_dataset.exporters.fpl import Namespaces, fpl_waypoint_types
from bas_air_unit_network_dataset.exporters.fpl.utils import (
    _upper_alphanumeric_only,
    _upper_alphanumeric_space_only,
)


class Waypoint:
    """
    FPL waypoint.

    Concrete representation of an abstract waypoint using the FPL output format.
    """

    max_identifier_length = 17
    max_country_code_length = 2
    max_comment_length = 25

    def __init__(
        self,
        identifier: Optional[str] = None,
        waypoint_type: Optional[str] = None,
        country_code: Optional[str] = None,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> None:
        """
        Create FPL waypoint, optionally setting parameters.

        :type identifier: str
        :param identifier: unique identifier
        :type waypoint_type: str
        :param waypoint_type: waypoint type, typically 'USER WAYPOINT'
        :type country_code: str
        :param country_code: two digit country code waypoint resides, or '__' for Antarctica
        :type longitude: float
        :param longitude: longitude component of waypoint geometry
        :type latitude: float
        :param latitude: latitude component of waypoint geometry
        :type comment: str
        :param comment: Optional comment/description
        """
        self.ns = Namespaces()

        self._identifier: str
        self._type: str
        self._country_code: str
        self._longitude: float
        self._latitude: float
        self._comment: Optional[str] = None

        if identifier is not None:
            self.identifier = identifier
        if waypoint_type is not None:
            self.waypoint_type = waypoint_type
        if country_code is not None:
            self.country_code = country_code
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        if comment is not None:
            self.comment = comment

    @property
    def identifier(self) -> str:
        """
        FPL waypoint identifier.

        :rtype: str
        :returns waypoint identifier
        """
        return self._identifier

    @identifier.setter
    def identifier(self, identifier: str) -> None:
        """
        Set FPL waypoint identifier.

        The FPL standard uses identifiers as foreign keys for referencing waypoints within routes, identifiers should
        therefore be unique values.

        The FPL standard restricts waypoint comments to 19 characters, however when listing waypoints, GPS devices may
        only display up to 17 characters. To avoid losing potentially crucial information, this library therefore
        considers 17 to be the effective limit, and will raise a ValueError exception if the length ia longer.

        Identifiers must consist of upper case alphanumeric characters (A-Z 0-9) only. Values containing invalid
        characters will be silently dropped.

        For example an identifier:
        > 'FOO-bar-ABCDEF' (14 characters)
        will become:
        > 'FOOABCDEF' (9 characters).

        :type identifier: str
        :param identifier: unique identifier
        """
        if len(identifier) > self.max_identifier_length:
            msg = f"Identifier must be {self.max_identifier_length} characters or less."
            raise ValueError(msg)
        self._identifier = _upper_alphanumeric_only(value=identifier)

    @property
    def waypoint_type(self) -> str:
        """
        FPL waypoint type.

        :rtype: str
        :returns waypoint type
        """
        return self._type

    @waypoint_type.setter
    def waypoint_type(self, waypoint_type: str) -> None:
        """
        Set FPL waypoint type.

        The FPL standard defines several types of waypoint defined in the `fpl_waypoint_types` list and which include:
        - "USER WAYPOINT": user defined
        - "AIRPORT": airport
        - "INT": intersection
        - "VOR": Very High Frequency Omnidirectional Station
        - etc.

        Note: This library does not validate any requirements that might apply to specific waypoint types, other than
        what may be specified in the FPL XML XSD. Where types other than 'USER WAYPOINT' are used, is likely an
        apparently valid FPL can be generated by this library but which is marked invalid when imported into a device.

        :type waypoint_type: str
        :param waypoint_type: waypoint type, typically 'USER WAYPOINT'
        """
        if waypoint_type not in fpl_waypoint_types:
            msg = f"Waypoint type must be one of {' '.join(fpl_waypoint_types)!r}"
            raise ValueError(msg)

        self._type = waypoint_type

    @property
    def country_code(self) -> str:
        """
        FPL waypoint country code.

        This value may use a double underscore ('__') to represent countries such as Antarctica.

        :rtype: str
        :return: waypoint country code
        """
        return self._country_code

    @country_code.setter
    def country_code(self, country_code: str) -> None:
        """
        Set country code for organising and finding waypoints.

        The FPL standard restricts country codes to 2 characters, which must consist of upper case alphanumeric
        characters (A-Z 0-9) only. Values containing invalid characters will be silently dropped, except where noted
        below.

        A double underscore ('__') is sometimes used as the country code for Antarctica, rather than it's ISO 2-digit
        country code, 'AQ' (see #157 for more information). This value is invalid according to the FPL standard but has
        been used successfully in devices so is allowed as an exception to comply with existing usage.
        :type country_code: str
        :param country_code: two digit country code waypoint resides, or '__' for Antarctica
        """
        if len(country_code) > self.max_country_code_length:
            msg = f"Country code must be {self.max_country_code_length} characters or less."
            raise ValueError(msg)

        self._country_code = _upper_alphanumeric_only(value=country_code)

        # As an exception for Antarctica, we use '__' as the country code
        if country_code == "__":
            self._country_code = "__"

    @property
    def longitude(self) -> float:
        """
        Longitude component of FPL waypoint geometry.

        :rtype: float
        :returns waypoint geometry longitude
        """
        return self._longitude

    @longitude.setter
    def longitude(self, longitude: float) -> None:
        """
        Set longitude component of waypoint geometry.

        The FPL standard assumes geometries are (single) points using the EPSG:4326 CRS. Values outside ±180 will raise
        a ValueError exception.

        **Note:** The FPL standard does not allow values to use `180.0` and `-180.0` exactly (for reasons best known to
        Garmin). This method will automatically convert values to be the closest values allowed (`±179.999999`).

        :type longitude: float
        :param longitude: longitude component of waypoint geometry
        """
        if -180 > longitude > 180:
            msg = "Longitude must be between -180 and +180."
            raise ValueError(msg)

        if longitude == -180:
            longitude = -179.999999
        elif longitude == 180:
            longitude = 179.999999

        self._longitude = longitude

    @property
    def latitude(self) -> float:
        """
        Latitude component of FPL waypoint geometry.

        :rtype: float
        :returns waypoint geometry latitude
        """
        return self._latitude

    @latitude.setter
    def latitude(self, latitude: float) -> None:
        """
        Set latitude component of waypoint geometry.

        The FPL standard assumes geometries are (single) points using the EPSG:4326 CRS. Values outside ±90 will raise
        a ValueError exception.

        **Note:** The FPL standard does not allow values to use `90.0` and `-90.0` exactly (for reasons best known to
        Garmin). This method will automatically convert values to be the closest values allowed (`±89.999999`).

        :type latitude: float
        :param latitude: latitude component of waypoint geometry
        """
        if -90 > latitude > 90:
            msg = "Latitude must be between -90 and +90."
            raise ValueError(msg)

        if latitude == 90:
            latitude = 89.999999
        elif latitude == -90:
            latitude = -89.999999

        self._latitude = latitude

    @property
    def comment(self) -> str:
        """
        FPL waypoint comment.

        :rtype: str
        :returns waypoint comment
        """
        if self._comment is None:
            return "NO COMMENT"
        return self._comment

    @comment.setter
    def comment(self, comment: str) -> None:
        """
        Set optional FPL waypoint comment.

        The FPL standard restricts waypoint comments to 25 characters, longer values will raise a ValueError exception.

        Comments must consist of upper case alphanumeric characters (A-Z 0-9), or spaces (' ') as a separator, only.
        Comments containing invalid characters will be silently dropped.

        For example a comment:
        > 'FOO-bar-ABC 123 DEF 456 G' (25 characters)
        will become:
        > 'FOOABC 123 DEF 456 G' (20 characters).

        :type comment: str
        :param comment: Optional comment/description
        """
        if len(comment) > self.max_comment_length:
            msg = f"Comments must be {self.max_comment_length} characters or less."
            raise ValueError(msg)

        self._comment = _upper_alphanumeric_space_only(value=comment)

    def encode(self) -> Element:
        """
        Build an XML element for the FPL waypoint.

        :rtype: Element
        :return: (L)XML element
        """
        waypoint = Element(f"{{{self.ns.fpl}}}waypoint", nsmap=self.ns.nsmap())

        identifier = SubElement(waypoint, f"{{{self.ns.fpl}}}identifier")
        identifier.text = self.identifier

        waypoint_type = SubElement(waypoint, f"{{{self.ns.fpl}}}type")
        waypoint_type.text = self.waypoint_type

        country_code = SubElement(waypoint, f"{{{self.ns.fpl}}}country-code")
        country_code.text = self.country_code

        latitude = SubElement(waypoint, f"{{{self.ns.fpl}}}lat")
        latitude.text = str(round(self.latitude, ndigits=7))

        longitude = SubElement(waypoint, f"{{{self.ns.fpl}}}lon")
        longitude.text = str(round(self.longitude, ndigits=7))

        if self.comment is not None:
            comment = SubElement(waypoint, f"{{{self.ns.fpl}}}comment")
            comment.text = self.comment

        return waypoint
