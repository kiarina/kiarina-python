from kiarina.agi.file_info import TextFileInfo
from kiarina.agi.file_info_builder import (
    BaseFileInfoBuilder,
    BuildResult,
    FileInfoSpec,
)
from kiarina.agi.run_context import RunContext
from kiarina.agi.token_utils import calc_text_token
from kiarina.utils.file import FileBlob, MarkdownContent

from .._utils.extract_text import extract_text


class TextFileInfoBuilder(BaseFileInfoBuilder):
    async def build(
        self,
        file_info_spec: FileInfoSpec,
        file_blob: FileBlob,
        *,
        run_context: RunContext,
    ) -> BuildResult:
        line_count = file_blob.raw_text.count("\n") + 1

        raw_text = extract_text(
            file_blob.raw_text,
            start_line=file_info_spec.get("start_line", 1),
            end_line=file_info_spec.get("end_line", -1),
        )

        token_count = calc_text_token(raw_text)

        if file_blob.mime_type == "text/markdown":
            markdown_content = MarkdownContent.from_text(file_blob.raw_text)

            if "name" in markdown_content.metadata:
                name = str(markdown_content.metadata["name"])
                name = name.replace('"', "").replace("'", "").strip()
                file_info_spec["name"] = name

            if "description" in markdown_content.metadata:
                description = str(markdown_content.metadata["description"])
                description = description.replace('"', "").replace("'", "").strip()
                description = description.replace("\n", "").strip()
                file_info_spec["description"] = description

        return BuildResult(
            file_info=TextFileInfo.model_validate(
                {
                    **file_info_spec,
                    # from file_blob
                    "mime_type": file_blob.mime_type,
                    "file_hash": file_blob.hash_string,
                    # from processing
                    "line_count": line_count,
                    "raw_text": raw_text
                    if not file_info_spec.get("metadata_only", False)
                    else None,
                    "file_size": 0,
                    "token_count": token_count,
                    "intermediate_file_path": None,
                    "asset_uri": None,
                }
            ),
            file_blob=file_blob,
        )
