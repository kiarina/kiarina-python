from .._instances.catalog import catalog
from .._models.translator import Translator
from .._settings import settings_manager
from .._types.i18n_scope import I18nScope
from .._types.language import Language


def get_translator(language: Language, scope: I18nScope) -> Translator:
    settings = settings_manager.settings
    return Translator(
        catalog=catalog,
        language=language,
        scope=scope,
        default_language=settings.default_language,
    )
