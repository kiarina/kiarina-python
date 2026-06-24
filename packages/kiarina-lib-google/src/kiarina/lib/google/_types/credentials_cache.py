from typing import Protocol

from .credentials_json_string import CredentialsJSONString


class CredentialsCache(Protocol):
    def get(self) -> CredentialsJSONString | None: ...

    def set(self, value: CredentialsJSONString) -> None: ...
