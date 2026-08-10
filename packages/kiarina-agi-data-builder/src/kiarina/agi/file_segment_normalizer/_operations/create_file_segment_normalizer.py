from kiarina.agi.file_info import FileType
from kiarina.agi.run_context import RunContext
from kiarina.utils.common import import_object

from .._settings import settings_manager
from .._types.file_segment_normalizer import FileSegmentNormalizer


def create_file_segment_normalizer(
    file_type: FileType,
    *,
    run_context: RunContext,
) -> FileSegmentNormalizer:
    settings = settings_manager.get_settings()

    if file_type in settings.normalizers:
        import_path = settings.normalizers[file_type]
    elif file_type in settings.presets:
        import_path = settings.presets[file_type]
    else:  # pragma: no cover
        raise ValueError(f"Normalizer is not registered: {file_type}")

    normalizer = import_object(import_path)(run_context)

    if not isinstance(normalizer, FileSegmentNormalizer):  # pragma: no cover
        raise ValueError(
            f"Imported object is not a FileSegmentNormalizer: {import_path}"
        )

    return normalizer
