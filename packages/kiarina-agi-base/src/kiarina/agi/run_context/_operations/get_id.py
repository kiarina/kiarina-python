from typing import Literal

from .._settings import settings_manager
from .._types.id_str import IDStr


def get_id(
    name: Literal["organization_id", "user_id", "agent_id", "node_id"],
) -> IDStr:
    settings = settings_manager.get_settings()
    value: IDStr | None = getattr(settings, name)

    if not value:
        raise ValueError(f"{name} is not set")
    if settings.disallow_default_ids and value == "default":
        raise ValueError(f"{name} must not be default")

    return value
