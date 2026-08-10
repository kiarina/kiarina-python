import os

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.file_info import ImageFileInfo
from kiarina.agi.file_info_builder import (
    BaseFileInfoBuilder,
    BuildResult,
    FileInfoSpec,
)
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext
from kiarina.agi.token_utils import calc_image_token
from kiarina.utils.file import FileBlob

from .._operations.build_intermediate_image import build_intermediate_image
from .._operations.get_image_size import get_image_size


class ImageFileInfoBuilder(BaseFileInfoBuilder):
    async def build(
        self,
        file_info_spec: FileInfoSpec,
        file_blob: FileBlob,
        *,
        run_context: RunContext,
    ) -> BuildResult:
        output_base_path = create_local_repository(run_context).generate_cache_path(
            os.path.join("intermediate", "image", file_blob.hash_string)
        )

        intermediate_file_path = await build_intermediate_image(
            file_blob.file_path, output_base_path
        )

        intermediate_file_blob: FileBlob | None = None

        if intermediate_file_path:
            intermediate_file_blob = await kfa.read_file(intermediate_file_path)

        target_blob = intermediate_file_blob or file_blob

        file_size = len(target_blob.raw_data)
        image_size = get_image_size(target_blob.raw_data)
        token_count = calc_image_token(image_size)

        return BuildResult(
            file_info=ImageFileInfo.model_validate(
                {
                    **file_info_spec,
                    # from file_blob
                    "mime_type": file_blob.mime_type,
                    "file_hash": file_blob.hash_string,
                    # from processing
                    "width": image_size.width,
                    "height": image_size.height,
                    "file_size": file_size,
                    "token_count": token_count,
                    "intermediate_file_path": intermediate_file_path,
                    "asset_uri": None,
                }
            ),
            file_blob=file_blob,
            intermediate_file_blob=intermediate_file_blob,
        )
