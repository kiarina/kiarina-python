from kiarina.agi.data.file_info_pool import FileInfoPool, dehydrate_file_infos

from .._models.content import Content


def dehydrate_content(
    content: Content,
    pool: FileInfoPool,
) -> tuple[Content, FileInfoPool]:
    new_file_infos, pool = dehydrate_file_infos(content.files, pool)

    if new_file_infos is content.files:
        return content, pool

    new_content = content.model_copy(update={"files": new_file_infos})
    return new_content, pool
