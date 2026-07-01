import logging
from importlib import import_module
from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._core.models.file_blob import FileBlob
    from ._core.types.markdown_content import MarkdownContent
    from ._sync.helpers.read_file import read_file
    from ._sync.helpers.read_markdown import read_markdown
    from ._sync.helpers.write_file import write_file
    from ._sync.utils.read_binary import read_binary
    from ._sync.utils.read_json_dict import read_json_dict
    from ._sync.utils.read_json_list import read_json_list
    from ._sync.utils.read_text import read_text
    from ._sync.utils.read_yaml_dict import read_yaml_dict
    from ._sync.utils.read_yaml_list import read_yaml_list
    from ._sync.utils.remove_file import remove_file
    from ._sync.utils.write_binary import write_binary
    from ._sync.utils.write_json_dict import write_json_dict
    from ._sync.utils.write_json_list import write_json_list
    from ._sync.utils.write_text import write_text
    from ._sync.utils.write_yaml_dict import write_yaml_dict
    from ._sync.utils.write_yaml_list import write_yaml_list

__version__ = version("kiarina-utils-file")

__all__ = [
    "FileBlob",
    "MarkdownContent",
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
]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        "FileBlob": "._core.models.file_blob",
        "MarkdownContent": "._core.types.markdown_content",
        "read_file": "._sync.helpers.read_file",
        "read_markdown": "._sync.helpers.read_markdown",
        "write_file": "._sync.helpers.write_file",
        "read_binary": "._sync.utils.read_binary",
        "read_json_dict": "._sync.utils.read_json_dict",
        "read_json_list": "._sync.utils.read_json_list",
        "read_text": "._sync.utils.read_text",
        "read_yaml_dict": "._sync.utils.read_yaml_dict",
        "read_yaml_list": "._sync.utils.read_yaml_list",
        "remove_file": "._sync.utils.remove_file",
        "write_binary": "._sync.utils.write_binary",
        "write_json_dict": "._sync.utils.write_json_dict",
        "write_json_list": "._sync.utils.write_json_list",
        "write_text": "._sync.utils.write_text",
        "write_yaml_dict": "._sync.utils.write_yaml_dict",
        "write_yaml_list": "._sync.utils.write_yaml_list",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
