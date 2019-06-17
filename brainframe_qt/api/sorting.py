from enum import Enum


class Ordering(Enum):
    """Specifies in what order a field should be sorted by."""
    ASC = "asc"
    DESC = "desc"


class SortOptions:
    """A sorting configuration. Used by some APIs that provide many of a
    certain object.
    """

    def __init__(self, field_name, ordering: Ordering):
        """
        :param field_name: The name of the field to sort by
        :param ordering: The order to sort the field by
        """
        self.field_name = field_name
        self.ordering = ordering

    def query_format(self) -> str:
        return f"{self.field_name}:{self.ordering.value}"
