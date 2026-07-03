from typing import Any

from .._models.gcs_asset_repository import GCSAssetRepository
from .._settings import GCSAssetRepositorySettings, settings_manager


def create_gcs_asset_repository(
    **kwargs: Any,
) -> GCSAssetRepository:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = GCSAssetRepositorySettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return GCSAssetRepository(settings)
