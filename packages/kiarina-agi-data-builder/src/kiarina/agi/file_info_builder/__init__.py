from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.build_file_info import build_file_info
    from ._helpers.rebuild_file_info import rebuild_file_info
    from ._models.base_file_info_builder import BaseFileInfoBuilder
    from ._schemas.build_result import BuildResult
    from ._services.file_info_builder_registry import file_info_builder_registry
    from ._settings import settings_manager
    from ._types.file_info_builder import FileInfoBuilder
    from ._types.file_info_builder_alias import FileInfoBuilderAlias
    from ._types.file_info_builder_name import FileInfoBuilderName
    from ._types.file_info_builder_specifier import FileInfoBuilderSpecifier
    from ._types.file_info_spec import FileInfoSpec
    from ._types.file_info_specifier import FileInfoSpecifier

__all__ = [
    # ._helpers
    "build_file_info",
    "rebuild_file_info",
    # ._models
    "BaseFileInfoBuilder",
    # ._services
    "file_info_builder_registry",
    # ._schemas
    "BuildResult",
    # ._settings
    "settings_manager",
    # ._types
    "FileInfoBuilderAlias",
    "FileInfoBuilder",
    "FileInfoBuilderName",
    "FileInfoBuilderSpecifier",
    "FileInfoSpec",
    "FileInfoSpecifier",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "build_file_info": "._helpers.build_file_info",
        "rebuild_file_info": "._helpers.rebuild_file_info",
        # ._models
        "BaseFileInfoBuilder": "._models.base_file_info_builder",
        # ._services
        "file_info_builder_registry": "._services.file_info_builder_registry",
        # ._schemas
        "BuildResult": "._schemas.build_result",
        # ._settings
        "settings_manager": "._settings",
        # ._types
        "FileInfoBuilderAlias": "._types.file_info_builder_alias",
        "FileInfoBuilder": "._types.file_info_builder",
        "FileInfoBuilderName": "._types.file_info_builder_name",
        "FileInfoBuilderSpecifier": "._types.file_info_builder_specifier",
        "FileInfoSpec": "._types.file_info_spec",
        "FileInfoSpecifier": "._types.file_info_specifier",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
