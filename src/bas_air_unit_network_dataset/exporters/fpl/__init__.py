from typing import ClassVar

fpl_waypoint_types = ["USER WAYPOINT", "AIRPORT", "NDB", "VOR", "INT", "INT-VRP"]


class Namespaces:
    """
    Namespaces for the Garmin FPL XML schema.

    This class defines XML namespaces and their corresponding schema (XSD) locations. It is a utility class to help
    generate encode FPL data in XML using the `lxml` library.
    """

    fpl = "http://www8.garmin.com/xmlschemas/FlightPlan/v1"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"

    _root_namespace = fpl

    _schema_locations: ClassVar[dict] = {
        "fpl": "http://www8.garmin.com/xmlschemas/FlightPlanv1.xsd",
    }

    namespaces: ClassVar[dict] = {
        "fpl": fpl,
        "xsi": xsi,
    }

    @staticmethod
    def nsmap(suppress_root_namespace: bool = False) -> dict:
        """
        Create a namespace map.

        Indexes namespaces by their prefix.

        E.g. {'xlink': 'http://www.w3.org/1999/xlink'}

        When a root namespace is set, a default namespace will be set by using the `None` constant for the relevant
        dict key (this is a lxml convention). This will create an invalid namespace map for use in XPath queries, this
        can be overcome using the `suppress_root_namespace` parameter, which will create a 'regular' map.

        :type suppress_root_namespace: bool
        :param suppress_root_namespace: When true, respects a root prefix as a default if set
        :return: dictionary of Namespaces indexed by prefix
        """
        nsmap = {}

        for prefix, namespace in Namespaces.namespaces.items():
            if namespace == Namespaces._root_namespace and not suppress_root_namespace:
                nsmap[None] = namespace
                continue

            nsmap[prefix] = namespace

        return nsmap

    @staticmethod
    def schema_locations() -> str:
        """
        Generate the value for a `xsi:schemaLocation` attribute.

        Defines the XML Schema Document (XSD) for each namespace in an XML tree

        E.g. 'xsi:schemaLocation="http://www.w3.org/1999/xlink https://www.w3.org/1999/xlink.xsd"'

        :rtype: str
        :return: schema location attribute value
        """
        schema_locations = ""
        for prefix, location in Namespaces._schema_locations.items():
            schema_locations = f"{schema_locations} {Namespaces.namespaces[prefix]} {location}"

        return schema_locations.lstrip()
