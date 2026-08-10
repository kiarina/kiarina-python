import os
from urllib.parse import parse_qs

from pydantic import BaseModel, Field

from .._types.local_path_pattern import LocalPathPattern


class LocalPathSpec(BaseModel):
    path_pattern: LocalPathPattern
    include_patterns: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(default_factory=list)

    @property
    def expanded_path_pattern(self) -> str:
        return os.path.expanduser(os.path.expandvars(self.path_pattern))

    @classmethod
    def from_string(cls, path_pattern: LocalPathPattern) -> "LocalPathSpec":
        idx = path_pattern.rfind("?")
        if idx == -1:
            return cls(path_pattern=path_pattern)

        suffix = path_pattern[idx + 1 :]
        if not (suffix.startswith("include=") or suffix.startswith("exclude=")):
            return cls(path_pattern=path_pattern)

        base_path_pattern, query = path_pattern[:idx], suffix
        params = parse_qs(query, keep_blank_values=True)

        include_patterns: list[str] = []

        if "include" in params:
            for value in params["include"]:
                include_patterns.extend(
                    part.strip() for part in value.split(",") if part.strip()
                )

        exclude_patterns: list[str] = []

        if "exclude" in params:
            for value in params["exclude"]:
                exclude_patterns.extend(
                    part.strip() for part in value.split(",") if part.strip()
                )

        return cls(
            path_pattern=base_path_pattern,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )
