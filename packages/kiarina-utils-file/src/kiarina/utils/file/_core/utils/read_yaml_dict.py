import os
from collections.abc import Awaitable
from typing import Any, Literal, overload

import yaml

from .read_text import read_text


@overload
def read_yaml_dict(
    mode: Literal["sync"],
    file_path: str | os.PathLike[str],
    *,
    default: dict[str, Any] | None = None,
) -> dict[str, Any] | None: ...


@overload
def read_yaml_dict(
    mode: Literal["async"],
    file_path: str | os.PathLike[str],
    *,
    default: dict[str, Any] | None = None,
) -> Awaitable[dict[str, Any] | None]: ...


def read_yaml_dict(
    mode: Literal["sync", "async"],
    file_path: str | os.PathLike[str],
    *,
    default: dict[str, Any] | None = None,
) -> dict[str, Any] | None | Awaitable[dict[str, Any] | None]:

    def _after(raw_text: str | None) -> dict[str, Any] | None:
        if raw_text is None:
            return default

        if not raw_text.strip():
            return default

        data = yaml.safe_load(raw_text)

        if data is None:
            return {} if default is None else default

        if not isinstance(data, dict):
            raise yaml.YAMLError("YAML data is not a dictionary")

        for key in data.keys():
            if not isinstance(key, str):
                raise yaml.YAMLError(
                    f"YAML dictionary contains non-string key: {key} (type: {type(key).__name__})"
                )

        return data

    def _sync() -> dict[str, Any] | None:
        raw_text = read_text("sync", file_path)
        return _after(raw_text)

    async def _async() -> dict[str, Any] | None:
        raw_text = await read_text("async", file_path)
        return _after(raw_text)

    if mode == "sync":
        return _sync()
    else:
        return _async()
