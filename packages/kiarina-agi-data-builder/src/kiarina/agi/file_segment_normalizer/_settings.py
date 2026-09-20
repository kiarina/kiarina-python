from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.file_segment_normalizer_name import FileSegmentNormalizerName


class FileSegmentNormalizerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_FILE_SEGMENT_NORMALIZER_",
        extra="ignore",
    )

    presets: dict[FileSegmentNormalizerName, ImportPath] = Field(
        default_factory=lambda: {
            "audio": "kiarina.agi.file_segment_normalizer_impl.audio:AudioFileSegmentNormalizer",
            "image": "kiarina.agi.file_segment_normalizer_impl.image:ImageFileSegmentNormalizer",
            "other": "kiarina.agi.file_segment_normalizer_impl.other:OtherFileSegmentNormalizer",
            "pdf": "kiarina.agi.file_segment_normalizer_impl.pdf:PDFFileSegmentNormalizer",
            "text": "kiarina.agi.file_segment_normalizer_impl.text:TextFileSegmentNormalizer",
            "video": "kiarina.agi.file_segment_normalizer_impl.video:VideoFileSegmentNormalizer",
        }
    )

    customs: dict[FileSegmentNormalizerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(FileSegmentNormalizerSettings)
