from bas_air_unit_network_dataset.models.category import Category, DEFAULT_CATEGORY_COLOUR, CATEGORY_COLOURS


class Categories:
    def __init__(self, categories: list[str]):
        self._categories: list[Category] = []
        self._make_categories(categories)

    def _make_categories(self, names: list[str]) -> None:
        unique_names_sorted = sorted(list(set(name for name in names if name is not None)))

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
        return self._categories

    @property
    def colours(self) -> dict[str, str]:
        return {category.slug: category.colour for category in self._categories}
