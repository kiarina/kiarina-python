from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._async.helpers.read_file import read_file
    from ._async.helpers.read_markdown import read_markdown
    from ._async.helpers.write_file import write_file
    from ._async.utils.read_binary import read_binary
    from ._async.utils.read_json_dict import read_json_dict
    from ._async.utils.read_json_list import read_json_list
    from ._async.utils.read_text import read_text
    from ._async.utils.read_yaml_dict import read_yaml_dict
    from ._async.utils.read_yaml_list import read_yaml_list
    from ._async.utils.remove_file import remove_file
    from ._async.utils.write_binary import write_binary
    from ._async.utils.write_json_dict import write_json_dict
    from ._async.utils.write_json_list import write_json_list
    from ._async.utils.write_text import write_text
    from ._async.utils.write_yaml_dict import write_yaml_dict
    from ._async.utils.write_yaml_list import write_yaml_list
    from ._core.models.file_blob import FileBlob
    from ._core.types.markdown_content import MarkdownContent

__all__ = [
    "read_file",
    "read_markdown",
    "write_file",
    "read_binary",
    "read_json_dict",
    "read_json_list",
    "read_text",
    "read_yaml_dict",
    "read_yaml_list",
    "remove_file",
    "write_binary",
    "write_json_dict",
    "write_json_list",
    "write_text",
    "write_yaml_dict",
    "write_yaml_list",
    "FileBlob",
    "MarkdownContent",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        "read_file": "._async.helpers.read_file",
        "read_markdown": "._async.helpers.read_markdown",
        "write_file": "._async.helpers.write_file",
        "read_binary": "._async.utils.read_binary",
        "read_json_dict": "._async.utils.read_json_dict",
        "read_json_list": "._async.utils.read_json_list",
        "read_text": "._async.utils.read_text",
        "read_yaml_dict": "._async.utils.read_yaml_dict",
        "read_yaml_list": "._async.utils.read_yaml_list",
        "remove_file": "._async.utils.remove_file",
        "write_binary": "._async.utils.write_binary",
        "write_json_dict": "._async.utils.write_json_dict",
        "write_json_list": "._async.utils.write_json_list",
        "write_text": "._async.utils.write_text",
        "write_yaml_dict": "._async.utils.write_yaml_dict",
        "write_yaml_list": "._async.utils.write_yaml_list",
        "FileBlob": "._core.models.file_blob",
        "MarkdownContent": "._core.types.markdown_content",
    }

    parent = __name__.rsplit(".", 1)[0]
    globals()[name] = getattr(import_module(module_map[name], parent), name)
    return globals()[name]
