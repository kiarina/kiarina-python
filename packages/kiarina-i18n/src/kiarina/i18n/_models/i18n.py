from typing import Any

from pydantic import BaseModel

from .._types.i18n_scope import I18nScope


class I18n(BaseModel):
    """
    Base class for i18n definitions.

    This class provides a type-safe way to define translation keys and default values.
    Subclasses can optionally define a scope using class inheritance parameter.
    If scope is not provided, it will be automatically generated from module and class name.

    Example:
        ```python
        from kiarina.i18n import I18n, get_i18n

        # Explicit scope
        class MyI18n(I18n, scope="my.module"):
            title: str = "My Title"
            description: str = "My Description"

        # Auto-generated scope (my.app.UserProfileI18n)
        class UserProfileI18n(I18n):
            name: str = "Name"
            email: str = "Email"

        # Get translated instance
        t = get_i18n(MyI18n, "ja")
        print(t.title)  # Translated title
        ```
    """

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
