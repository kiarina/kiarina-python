from typing import Any

from pydantic import BaseModel

from .._types.i18n_scope import I18nScope


class I18n(BaseModel):
    """Base model for typed translation keys and their default text."""

    _scope: I18nScope = ""

    def __init_subclass__(cls, scope: I18nScope = "", **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if scope:
            cls._scope = scope
        else:
            cls._scope = f"{cls.__module__}.{cls.__name__}"

    model_config = {
        "frozen": True,
        "extra": "forbid",
    }
