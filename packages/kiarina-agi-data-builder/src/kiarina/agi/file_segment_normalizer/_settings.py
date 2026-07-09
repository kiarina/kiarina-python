from typing import cast

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.file_info import FileType
from kiarina.utils.common import ImportPath


class FileSegmentNormalizerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_FILE_SEGMENT_NORMALIZER_",
        extra="ignore",
    )

    presets: dict[FileType, ImportPath] = Field(
        default_factory=lambda: cast(
            dict[FileType, ImportPath],
            {
                "audio": "kiarina.agi.file_segment_normalizer_impl.audio:AudioFileSegmentNormalizer",
                "image": "kiarina.agi.file_segment_normalizer_impl.image:ImageFileSegmentNormalizer",
                "other": "kiarina.agi.file_segment_normalizer_impl.other:OtherFileSegmentNormalizer",
                "pdf": "kiarina.agi.file_segment_normalizer_impl.pdf:PDFFileSegmentNormalizer",
                "text": "kiarina.agi.file_segment_normalizer_impl.text:TextFileSegmentNormalizer",
                "video": "kiarina.agi.file_segment_normalizer_impl.video:VideoFileSegmentNormalizer",
            },
        )
    )

    normalizers: dict[FileType, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(FileSegmentNormalizerSettings)
