import os

import pytest

from kiarina.agi.data.file_info import BaseFileInfo, OtherFileInfo


@pytest.fixture
def file_info() -> OtherFileInfo:
    return OtherFileInfo(
        uri_or_file_path="http://example.com/file.txt",
        mime_type="text/plain",
        file_hash="dummy-hash",
        file_size=1,
        token_count=0,
        intermediate_file_path=None,
        asset_uri=None,
    )


def test_normalize_file_path() -> None:
    file_info = OtherFileInfo(
        uri_or_file_path="./test.txt",
        mime_type="text/plain",
        file_hash="dummy-hash",
        file_size=1,
        token_count=0,
        intermediate_file_path=None,
        asset_uri=None,
    )

    assert file_info.uri_or_file_path == os.path.abspath("./test.txt")


def test_prepared(file_info: BaseFileInfo) -> None:
    assert file_info.prepared

    file_info.asset_uri = "asset://" + file_info.uri_or_file_path
    assert file_info.prepared

    file_info.asset_uri = None
    file_info.intermediate_file_path = "/path/to/intermediate/file"
    assert not file_info.prepared

    file_info.intermediate_file_path = None
    file_info.uri_or_file_path = f"file://{file_info.uri_or_file_path}"
    assert file_info.prepared


def test_xml_attributes(file_info: BaseFileInfo) -> None:
    attrs = file_info.xml_attributes

    assert "id" in attrs
    assert "name" not in attrs
    assert "description" not in attrs
    assert "uri" in attrs
    assert "file_path" not in attrs


def test_export(file_info: BaseFileInfo) -> None:
    exported = file_info.export()
    print("exported:", exported)

    assert exported.pop("id") == file_info.id
    assert exported.pop("created_at") == file_info.created_at.isoformat()
    assert exported.pop("uri_or_file_path") == file_info.uri_or_file_path
    assert "name" not in exported
    assert "description" not in exported
    assert "pinned" not in exported
    assert "inline" not in exported
    assert "metadata_only" not in exported
    assert "content_only" not in exported
    assert "no_merge" not in exported
    assert "group" not in exported
    assert "unique_key" not in exported
    assert "keep_from_end" not in exported
    assert "tag" not in exported
    assert "default_template" not in exported
    assert "metadata_only_template" not in exported
    assert not exported


def test_to_estimates(file_info: BaseFileInfo) -> None:
    print("to_estimates:", file_info.to_estimates())
    print("to_metadata_estimates:", file_info.to_metadata_estimates())
    print("to_content_estimates:", file_info.to_content_estimates())


def test_shrink_metadata_only(text_file_info: BaseFileInfo) -> None:
    file_info = text_file_info.as_metadata_only()
    new_file_info, reduced = file_info.shrink(reduce=10)
    assert new_file_info is file_info
    assert reduced == 0


def test_shrink_reserve(text_file_info: BaseFileInfo) -> None:
    new_file_info, reduced = text_file_info.shrink(
        reduce=10, reserve=text_file_info.token_count
    )
    assert new_file_info is text_file_info
    assert reduced == 0


def test_shrink(image_file_info: BaseFileInfo) -> None:
    new_file_info, reduced = image_file_info.shrink(reduce=10)
    assert new_file_info.metadata_only
    assert reduced == image_file_info.token_count


def test_get_field_value(text_file_info: BaseFileInfo) -> None:
    assert text_file_info.get_value("tag") is None

    text_file_info.tag = "custom_tag"
    assert text_file_info.get_value("tag") == "custom_tag"
