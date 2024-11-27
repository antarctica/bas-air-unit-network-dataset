from dataclasses import dataclass

from slugify import slugify

DEFAULT_CATEGORY_COLOUR = "#a3a3a3"  # neutral-400
CATEGORY_COLOURS = [
    "#ef4444",  # red
    "#f97316",  # orange
    # "#f59e0b",  # amber (disabled, too similar to yellow)  # noqa: ERA001
    "#eab308",  # yellow
    "#84cc16",  # lime
    # "#22c55e",  # green (disabled, too similar to emerald)
    "#10b981",  # emerald
    "#14b8a6",  # teal
    "#06b6d4",  # cyan
    "#0ea5e9",  # sky
    "#3b82f6",  # blue
    "#6366f1",  # indigo
    "#8b5cf6",  # violet
    "#a855f7",  # purple
    "#d946ef",  # fuchsia
    "#ec4899",  # pink
    "#f43f5e",  # rose
]


@dataclass
class Category:
    """A label used to group or categorise a set of waypoints."""

    name: str
    colour: str = DEFAULT_CATEGORY_COLOUR
    weight: float = 0.4

    def __post_init__(self) -> None:
        self.slug = slugify(self.name)
