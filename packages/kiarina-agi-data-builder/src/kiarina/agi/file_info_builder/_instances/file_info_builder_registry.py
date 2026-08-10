from kiarina.utils.component_registry import ComponentRegistry

from .._settings import settings_manager
from .._types.file_info_builder import FileInfoBuilder

file_info_builder_registry = ComponentRegistry[FileInfoBuilder](
    expected_type=FileInfoBuilder,
    component_label="FileInfoBuilder",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
)
