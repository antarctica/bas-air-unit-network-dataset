from bas_air_unit_network_dataset.models.category import CATEGORY_COLOURS, DEFAULT_CATEGORY_COLOUR, Category


class Categories:
    """A collection/set of categories."""

    def __init__(self, categories: list[str]) -> None:
        self._categories: list[Category] = []
        self._make_categories(categories)

    def _make_categories(self, names: list[str]) -> None:
        unique_names_sorted = sorted({name for name in names if name is not None})

        for i, name in enumerate(unique_names_sorted):
            try:
                colour = CATEGORY_COLOURS[i]
            except IndexError:
                colour = DEFAULT_CATEGORY_COLOUR

            self._categories.append(Category(name=name, colour=colour))

    @property
    def _slugs(self) -> list[str]:
        return [category.slug for category in self._categories]

    @property
    def as_list(self) -> list[Category]:
        """Get categories as a list of objects."""
        return self._categories

    @property
    def colours(self) -> dict[str, str]:
        """Get categories as a dict where keys are category slugs and values are the assigned colour value."""
        return {category.slug: category.colour for category in self._categories}
