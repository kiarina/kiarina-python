from typing import Any

import numpy as np

from kiarina.lib.redisearch_schema import RedisearchSchema


def marshal_mappings(
    *,
    schema: RedisearchSchema,
    mapping: dict[str, Any],
) -> dict[str, Any]:
    marshaled: dict[str, Any] = {}

    for key, value in mapping.items():
        field = schema.get_field(key)

        if not field:
            marshaled[key] = value
            continue

        if field.type == "tag":
            if isinstance(value, (list, tuple)):
                if not field.multiple:
                    raise ValueError(
                        f"Field '{key}' does not allow multiple tags. Got: {value}"
                    )

                marshaled[key] = field.separator.join(str(v) for v in value)
            else:
                marshaled[key] = str(value)

        elif field.type == "numeric":
            try:
                marshaled[key] = float(value)
            except (TypeError, ValueError) as e:
                raise ValueError(
                    f"Field '{key}' requires a numeric value. Got: {value}"
                ) from e

        elif field.type == "text":
            marshaled[key] = str(value)

        elif field.type == "vector":
            if not isinstance(value, list) or not all(
                isinstance(v, (float, int)) for v in value
            ):
                raise ValueError(
                    f"Field '{key}' requires a list of floats. Got: {value}"
                )

            marshaled[key] = np.array(value).astype(field.dtype).tobytes()

    return marshaled
