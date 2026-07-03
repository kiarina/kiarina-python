from .._settings import settings_manager


def get_node_id() -> str:
    return settings_manager.get_settings().get_node_id()
