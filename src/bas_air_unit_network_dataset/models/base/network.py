from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bas_air_unit_network_dataset.models.base.route import Route
    from bas_air_unit_network_dataset.models.base.waypoint import Waypoint


class Network:
    """
    A collection of Waypoints and Routes.

    A network is a logical set of Waypoints and Routes for a given purpose or context. For example, a global or
    regional logistics network, a science project, etc.

    The Network class provides a waypoints and route collection, along with methods for loading features at a network
    level.

    Intended as a base class for network specific classes with specific naming conventions or other conventions.
    """

    def __init__(self, waypoints: list[Waypoint] | None = None, routes: list[Route] | None = None) -> None:
        self._waypoints = waypoints or []
        self._routes = routes or []

    def __repr__(self) -> str:
        """String representation."""
        return f"<Network : {len(self._waypoints)} Waypoints - {len(self._routes)} Routes>"

    def display(self) -> str:
        """Information about a network."""
        waypoints_zfill = len(str(len(self._waypoints)))
        routes_zfill = len(str(len(self._routes)))

        lines = [repr(self), "\n", f"Waypoints [{len(self._waypoints)}]:"]
        lines.extend(
            [f"{str(i + 1).zfill(waypoints_zfill)}. {waypoint}\n" for i, waypoint in enumerate(self._waypoints)]
        )
        lines.extend(["\n", f"Routes [{len(self._routes)}]:"])
        lines.extend([f"{str(i + 1).zfill(routes_zfill)}. {route}\n" for i, route in enumerate(self._routes)])
        return "".join(lines)
