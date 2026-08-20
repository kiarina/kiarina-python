from kiarina.utils.object_registry import ObjectRegistry

from .._services.token_manager import TokenManager

token_manager_registry = ObjectRegistry[TokenManager, None](
    expected_type=TokenManager,
    object_label="TokenManager",
)
