from typing import TypeAlias

from .asset_repository_name import AssetRepositoryName

AssetRepositorySpecifier: TypeAlias = AssetRepositoryName | str
"""
A string in the form of "{AssetRepositoryName}?{ConfigString}"

Examples:
- "local"
- "gcs"
- "gcs?google_auth_settings_key=service_account"
"""
