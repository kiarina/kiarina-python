from typing import TypeVar

from pydantic import BaseModel

from .._types.language import Language
from .get_system_language import get_system_language
from .get_translator import get_translator
from .resolve_i18n_scope import resolve_i18n_scope

T = TypeVar("T", bound=BaseModel)


def get_i18n(model_class: type[T], language: Language | None = None) -> T:
    """
    Get translated Pydantic model instance.

    This function creates an instance of the given model class with all fields
    translated to the specified language.

    Args:
        model_class: Pydantic model class to instantiate (not instance!)
        language: Target BCP 47 language tag (e.g., "en", "ja-JP").
            If omitted, the system language is detected automatically.

    Returns:
        Translated model instance with all fields translated

    Example:
        ```python
        from pydantic import BaseModel
        from kiarina.i18n import I18n, get_i18n

        class MyI18n(I18n, scope="my.module"):
            title: str = "My Title"
            description: str = "My Description"

        class PublicModel(BaseModel):
            title: str = "My Title"
            description: str = "My Description"

        # Get translated instance
        t = get_i18n(MyI18n, "ja")
        print(t.title)  # Translated title in Japanese
        print(t.description)  # Translated description in Japanese
        ```
    """
    scope = resolve_i18n_scope(model_class)
    target_language = language or get_system_language()

    default_instance = model_class.model_construct()
    translator = get_translator(target_language, scope)

    translated_data = {}

    for field_name in model_class.model_fields:
        default_value = getattr(default_instance, field_name)
        translated_data[field_name] = translator(field_name, default=default_value)

    return model_class(**translated_data)
