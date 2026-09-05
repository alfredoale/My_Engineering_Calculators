from numbers import Number
from typing import Any


def table_columns(records: list[dict[str, Any]]) -> list[str]:
    """Return columns in the order in which they first appear."""
    columns = []
    seen = set()
    for record in records:
        for column in record:
            if column not in seen:
                columns.append(column)
                seen.add(column)
    return columns


def column_values(records: list[dict[str, Any]], column: str) -> list[Any]:
    """Return non-null values for a column, preserving their original order."""
    return [record[column] for record in records if record.get(column) is not None]


def sort_filter_options(values: list[Any]) -> list[Any]:
    """Sort numeric values first, followed by other values alphabetically."""
    unique_values = list(dict.fromkeys(values))
    return sorted(
        unique_values,
        key=lambda value: (
            0,
            value,
        ) if isinstance(value, Number) and not isinstance(value, bool) else (
            1,
            str(value).casefold(),
            str(value),
        ),
    )


def is_numeric_column(records: list[dict[str, Any]], column: str) -> bool:
    """Return whether a non-empty column contains only numeric, non-boolean values."""
    values = column_values(records, column)
    return bool(values) and all(isinstance(value, Number) and not isinstance(value, bool) for value in values)


def filter_table_records(
    records: list[dict[str, Any]],
    search: str = "",
    column_filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Return records matching the search text and every column criterion.

    Search text matches any non-null value. Criteria may be inclusive ranges
    represented by tuples, exact value sets, or case-insensitive substrings.
    The input list and its row objects are left unchanged.
    """
    normalized_search = search.strip().casefold()
    column_filters = column_filters or {}

    def matches(record: dict[str, Any]) -> bool:
        if normalized_search and not any(
            normalized_search in str(value).casefold()
            for value in record.values()
            if value is not None
        ):
            return False

        for column, criterion in column_filters.items():
            value = record.get(column)
            if isinstance(criterion, tuple):
                if value is None or not criterion[0] <= value <= criterion[1]:
                    return False
            elif isinstance(criterion, set):
                if value not in criterion:
                    return False
            elif criterion and (value is None or criterion.casefold() not in str(value).casefold()):
                return False
        return True

    return [record for record in records if matches(record)]