from kiarina.utils.component_registry import ComponentRegistry

from .._settings import settings_manager
from .._types.file_segment_normalizer import FileSegmentNormalizer

file_segment_normalizer_registry = ComponentRegistry[FileSegmentNormalizer](
    expected_type=FileSegmentNormalizer,
    component_label="FileSegmentNormalizer",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
)
