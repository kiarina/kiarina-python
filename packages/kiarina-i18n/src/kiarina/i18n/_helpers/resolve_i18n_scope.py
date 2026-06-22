from pydantic import BaseModel

from .._models.i18n import I18n
from .._types.i18n_scope import I18nScope


def resolve_i18n_scope(model_class: type[BaseModel]) -> I18nScope:
    if issubclass(model_class, I18n):
        return model_class._scope

    return _get_public_module(model_class.__module__)


def _get_public_module(module: str) -> I18nScope:
    words = module.split(".")

    for index, word in enumerate(words):
        if word.startswith("_"):
            return ".".join(words[:index])

    return module
