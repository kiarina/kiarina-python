from kiarina.agi.content import Content
from kiarina.agi.file_info_loader import load_file_infos
from kiarina.agi.run_context import RunContext

from .._types.content_input import ContentInput


async def build_content(
    content_input: ContentInput,
    *,
    run_context: RunContext,
) -> Content:
    if isinstance(content_input, Content):
        return content_input

    if isinstance(content_input, str):
        content_input = {"text": content_input}

    if "files" in content_input:
        content_input["files"] = await load_file_infos(
            content_input["files"], run_context=run_context
        )

    return Content.model_validate(content_input)
