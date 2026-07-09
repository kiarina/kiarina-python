from typing import cast

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.file_info_builder_alias import FileInfoBuilderAlias
from ._types.file_info_builder_name import FileInfoBuilderName
from ._types.file_info_builder_specifier import FileInfoBuilderSpecifier


class FileBuilderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_FILE_BUILDER_",
        extra="ignore",
    )

    default: FileInfoBuilderSpecifier | None = None

    aliases: dict[FileInfoBuilderAlias, FileInfoBuilderName] = Field(
        default_factory=lambda: {
            "audio": "audio",
            "image": "image",
            "other": "other",
            "pdf": "pdf",
            "text": "text",
            "video": "video",
        }
    )

    presets: dict[FileInfoBuilderName, ImportPath] = Field(
        default_factory=lambda: cast(
            dict[FileInfoBuilderName, ImportPath],
            {
                "audio": "kiarina.agi.file_info_builder_impl.audio:create_audio_file_info_builder",
                "image": "kiarina.agi.file_info_builder_impl.image:ImageFileInfoBuilder",
                "other": "kiarina.agi.file_info_builder_impl.other:OtherFileInfoBuilder",
                "pdf": "kiarina.agi.file_info_builder_impl.pdf:PDFFileInfoBuilder",
                "text": "kiarina.agi.file_info_builder_impl.text:TextFileInfoBuilder",
                "video": "kiarina.agi.file_info_builder_impl.video:VideoFileInfoBuilder",
            },
        )
    )

    customs: dict[FileInfoBuilderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(FileBuilderSettings)
