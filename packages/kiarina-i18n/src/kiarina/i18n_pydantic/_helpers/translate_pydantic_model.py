from copy import deepcopy
from typing import Any, TypeVar, get_args, get_origin

from pydantic import BaseModel, create_model

from ...i18n._helpers.get_translator import get_translator
from ...i18n._helpers.resolve_i18n_scope import resolve_i18n_scope
from ...i18n._models.i18n import I18n

T = TypeVar("T", bound=BaseModel)


def translate_pydantic_model(
    model: type[T],
    language: str,
) -> type[T]:
    scope = resolve_i18n_scope(model)
    translator = get_translator(language, scope)

    original_doc = model.__doc__ or ""
    translated_doc = translator("__doc__", default=original_doc)

    new_fields: dict[str, Any] = {}

    for field_name, field_info in model.model_fields.items():
        original_desc = field_info.description or ""
        translated_desc = translator(field_name, default=original_desc)

        new_field_info = deepcopy(field_info)
        new_field_info.description = translated_desc

        translated_annotation = _translate_nested_model(field_info.annotation, language)

        new_fields[field_name] = (translated_annotation, new_field_info)

    translated_model = create_model(
        model.__name__,
        __config__=model.model_config,
        __doc__=translated_doc,
        __base__=model.__base__,
        __module__=model.__module__,
        **new_fields,
    )

    return translated_model  # type: ignore


def _translate_nested_model(
    annotation: Any,
    language: str,
) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is list and len(args) == 1:
        inner_type = args[0]
        if isinstance(inner_type, type) and issubclass(inner_type, I18n):
            translated_inner = translate_pydantic_model(inner_type, language)
            return list[translated_inner]  # type: ignore

    if origin is dict and len(args) == 2:
        key_type, value_type = args
        if (
            key_type is str
            and isinstance(value_type, type)
            and issubclass(value_type, I18n)
        ):
            translated_value = translate_pydantic_model(value_type, language)
            return dict[str, translated_value]  # type: ignore

    return annotation
