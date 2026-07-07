import logging
from importlib import import_module
from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.get_credentials import get_credentials
    from ._helpers.get_genai_options import get_genai_options
    from ._helpers.get_self_signed_jwt import get_self_signed_jwt
    from ._settings import GoogleSettings, settings_manager
    from ._types.credentials import Credentials
    from ._types.credentials_cache import CredentialsCache
    from ._types.credentials_json_string import CredentialsJSONString
    from ._types.self_signed_jwt import SelfSignedJWT
    from ._utils.get_default_credentials import get_default_credentials
    from ._utils.get_service_account_credentials import get_service_account_credentials
    from ._utils.get_user_account_credentials import get_user_account_credentials

__version__ = version("kiarina-lib-google")

__all__ = [
    # ._helpers
    "get_credentials",
    "get_genai_options",
    "get_self_signed_jwt",
    # ._settings
    "GoogleSettings",
    "settings_manager",
    # ._types
    "Credentials",
    "CredentialsCache",
    "CredentialsJSONString",
    "SelfSignedJWT",
    # ._utils
    "get_default_credentials",
    "get_service_account_credentials",
    "get_user_account_credentials",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        # ._helpers
        "get_credentials": "._helpers.get_credentials",
        "get_genai_options": "._helpers.get_genai_options",
        "get_self_signed_jwt": "._helpers.get_self_signed_jwt",
        # ._settings
        "GoogleSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "Credentials": "._types.credentials",
        "CredentialsCache": "._types.credentials_cache",
        "CredentialsJSONString": "._types.credentials_json_string",
        "SelfSignedJWT": "._types.self_signed_jwt",
        # ._utils
        "get_default_credentials": "._utils.get_default_credentials",
        "get_service_account_credentials": "._utils.get_service_account_credentials",
        "get_user_account_credentials": "._utils.get_user_account_credentials",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
