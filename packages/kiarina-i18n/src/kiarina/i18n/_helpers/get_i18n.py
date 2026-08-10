from typing import TypeVar

from pydantic import BaseModel

from .._types.language import Language
from .get_system_language import get_system_language
from .get_translator import get_translator
from .resolve_i18n_scope import resolve_i18n_scope

T = TypeVar("T", bound=BaseModel)


def get_i18n(model_class: type[T], language: Language | None = None) -> T:
    scope = resolve_i18n_scope(model_class)
    target_language = language or get_system_language()

    default_instance = model_class.model_construct()
    translator = get_translator(target_language, scope)

    translated_data = {}

    for field_name in model_class.model_fields:
        default_value = getattr(default_instance, field_name)
        translated_data[field_name] = translator(field_name, default=default_value)

    return model_class(**translated_data)
