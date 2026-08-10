from kiarina.lib.redisearch_schema import RedisearchSchema

from .._models.numeric import Numeric
from .._models.redisearch_filter import RedisearchFilter
from .._models.tag import Tag
from .._models.text import Text
from .._types.redisearch_filter_conditions import RedisearchFilterConditions


def create_redisearch_filter(
    *,
    filter: RedisearchFilter | RedisearchFilterConditions,
    schema: RedisearchSchema,
) -> RedisearchFilter | None:
    if isinstance(filter, RedisearchFilter):
        return filter

    conditions = filter

    filters: list[RedisearchFilter] = []

    for condition in conditions:
        if len(condition) != 3:
            raise ValueError("Each condition must have exactly 3 elements")

        field_name = condition[0]

        if not isinstance(field_name, str):
            raise ValueError("Field name must be a string")

        field = schema.get_field(field_name)

        if field is None:
            raise ValueError(f"Field '{field_name}' not found in schema")

        if field.type == "tag":
            filters.append(_create_tag_filter(condition))
        elif field.type == "numeric":
            filters.append(_create_numeric_filter(condition))
        elif field.type == "text":
            filters.append(_create_text_filter(condition))
        else:
            raise ValueError(
                f"Unsupported field type: {field.type}, field: {field_name}"
            )

    if not filters:
        return None

    return _combine_filters(filters)


def _create_tag_filter(condition: list[str | tuple[str]]) -> RedisearchFilter:
    field, operator, values = condition

    tag_field = Tag(str(field))

    result: RedisearchFilter

    if operator == "==" or operator == "=":
        result = tag_field == values
    elif operator == "!=":
        result = tag_field != values
    elif operator == "in":
        result = tag_field == values
    elif operator == "not in":
        result = tag_field != values
    else:
        raise ValueError(f"Invalid operator: {operator}")

    return result


def _create_numeric_filter(condition: list[str | int | float]) -> RedisearchFilter:
    field, operator, value = condition

    if isinstance(value, str):
        raise ValueError("Numeric value must be int or float")

    numeric_field = Numeric(str(field))

    result: RedisearchFilter

    if operator == "==" or operator == "=":
        result = numeric_field == value
    elif operator == "!=":
        result = numeric_field != value
    elif operator == ">":
        result = numeric_field > value
    elif operator == "<":
        result = numeric_field < value
    elif operator == ">=":
        result = numeric_field >= value
    elif operator == "<=":
        result = numeric_field <= value
    else:
        raise ValueError(f"Invalid operator: {operator}")

    return result


def _create_text_filter(condition: list[str]) -> RedisearchFilter:
    field, operator, value = condition

    text_field = Text(str(field))
    value = str(value)
    result: RedisearchFilter

    if operator == "==" or operator == "=":
        result = text_field == value
    elif operator == "!=":
        result = text_field != value
    elif operator == "%" or operator == "like":
        result = text_field % value
    else:
        raise ValueError(f"Invalid operator: {operator}")

    return result


def _combine_filters(filters: list[RedisearchFilter]) -> RedisearchFilter:
    combined = filters[0]

    for filter in filters[1:]:
        combined = combined & filter

    return combined
