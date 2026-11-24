from datetime import date

from jinja2 import Environment, PackageLoader

from bas_air_unit_network_dataset.models.base.categories import Categories
from bas_air_unit_network_dataset.models.formats.html import WaypointsReportWaypoint


class WaypointsReport:
    """
    Waypoints report.

    Generates a pre-formatted table based report of waypoints grouped by category.

    The revision date identifies when the source data was last updated.
    """

    templates_ref = "bas_air_unit_network_dataset.resources.templates"
    template_name = "air_unit_waypoints.j2"
    title = "Air Unit Waypoints"

    def __init__(self, waypoints: list[WaypointsReportWaypoint], revision_date: date) -> None:
        self._jinja = Environment(
            loader=PackageLoader(package_name="bas_air_unit_network_dataset.exporters.html", package_path="templates"),
            autoescape=True,
        )
        self._waypoints = waypoints
        self._revision_date = revision_date

    @property
    def _categories(self) -> Categories:
        """Get category objects for waypoints in collection."""
        categories = [waypoint.category for waypoint in self._waypoints]
        return Categories(categories)

    @property
    def _item_categories(self) -> list[dict]:
        """Structure waypoints into per-category lists."""
        categories = []
        for category in self._categories.as_list:
            categories.append({"category": category, "rows": self._report_waypoints_in_category(category.name)})
        return categories

    @property
    def _meta(self) -> dict:
        """Template context."""
        return {
            "title": self.title,
            "revision_date": self._revision_date.isoformat(),
            "template": self.template_name,
            "category_colours": self._categories.colours,
        }

    def _report_waypoints_in_category(self, category: str) -> list[WaypointsReportWaypoint]:
        """Filter waypoints by category."""
        return [waypoint for waypoint in self._waypoints if waypoint.category == category]

    def dumps(self) -> str:
        """Generate HTML content using a Jinja template."""
        template = self._jinja.get_template(self.template_name)
        return template.render(items=self._waypoints, item_categories=self._item_categories, meta=self._meta)
