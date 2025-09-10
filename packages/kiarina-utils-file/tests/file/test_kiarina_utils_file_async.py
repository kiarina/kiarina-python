import os
import tempfile

import pytest

import kiarina.utils.file.asyncio as kfa


@pytest.mark.asyncio
async def test_main():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. write_binary
        binary_path = os.path.join(tmp_dir, "test.bin")
        binary_data = b"Hello, binary world!"
        await kfa.write_binary(binary_path, binary_data)

        # 2. read_binary
        read_binary_data = await kfa.read_binary(binary_path)
        assert read_binary_data == binary_data

        # Test read_binary with default
        non_existent_path = os.path.join(tmp_dir, "non_existent.bin")
        assert await kfa.read_binary(non_existent_path) is None
        assert (
            await kfa.read_binary(non_existent_path, default=b"default") == b"default"
        )

        # 3. write_text
        text_path = os.path.join(tmp_dir, "test.txt")
        text_data = "Hello, text world! 日本語テスト"
        await kfa.write_text(text_path, text_data)

        # 4. read_text
        read_text_data = await kfa.read_text(text_path)
        assert read_text_data == text_data

        # Test read_text with default
        non_existent_text_path = os.path.join(tmp_dir, "non_existent.txt")
        assert await kfa.read_text(non_existent_text_path) is None
        assert (
            await kfa.read_text(non_existent_text_path, default="default") == "default"
        )

        # 5. write_json_list
        json_list_path = os.path.join(tmp_dir, "test_list.json")
        json_list_data = [1, 2, "three", {"four": 4}, [5, 6]]
        await kfa.write_json_list(json_list_path, json_list_data)

        # 6. read_json_list
        read_json_list_data = await kfa.read_json_list(json_list_path)
        assert read_json_list_data == json_list_data

        # Test read_json_list with default
        non_existent_json_list_path = os.path.join(tmp_dir, "non_existent_list.json")
        assert await kfa.read_json_list(non_existent_json_list_path) is None
        assert await kfa.read_json_list(non_existent_json_list_path, default=[]) == []

        # 7. write_json_dict
        json_dict_path = os.path.join(tmp_dir, "test_dict.json")
        json_dict_data = {"name": "Alice", "age": 30, "hobbies": ["reading", "coding"]}
        await kfa.write_json_dict(json_dict_path, json_dict_data)

        # 8. read_json_dict
        read_json_dict_data = await kfa.read_json_dict(json_dict_path)
        assert read_json_dict_data == json_dict_data

        # Test read_json_dict with default
        non_existent_json_dict_path = os.path.join(tmp_dir, "non_existent_dict.json")
        assert await kfa.read_json_dict(non_existent_json_dict_path) is None
        assert await kfa.read_json_dict(non_existent_json_dict_path, default={}) == {}

        # 9. write_yaml_list
        yaml_list_path = os.path.join(tmp_dir, "test_list.yaml")
        yaml_list_data = [1, 2, "three", {"four": 4}, [5, 6]]
        await kfa.write_yaml_list(yaml_list_path, yaml_list_data)

        # 10. read_yaml_list
        read_yaml_list_data = await kfa.read_yaml_list(yaml_list_path)
        assert read_yaml_list_data == yaml_list_data

        # Test read_yaml_list with default
        non_existent_yaml_list_path = os.path.join(tmp_dir, "non_existent_list.yaml")
        assert await kfa.read_yaml_list(non_existent_yaml_list_path) is None
        assert await kfa.read_yaml_list(non_existent_yaml_list_path, default=[]) == []

        # 11. write_yaml_dict
        yaml_dict_path = os.path.join(tmp_dir, "test_dict.yaml")
        yaml_dict_data = {"name": "Bob", "age": 25, "skills": ["python", "yaml"]}
        await kfa.write_yaml_dict(yaml_dict_path, yaml_dict_data)

        # 12. read_yaml_dict
        read_yaml_dict_data = await kfa.read_yaml_dict(yaml_dict_path)
        assert read_yaml_dict_data == yaml_dict_data

        # Test read_yaml_dict with default
        non_existent_yaml_dict_path = os.path.join(tmp_dir, "non_existent_dict.yaml")
        assert await kfa.read_yaml_dict(non_existent_yaml_dict_path) is None
        assert await kfa.read_yaml_dict(non_existent_yaml_dict_path, default={}) == {}

        # 13. write_file
        file_blob = kfa.FileBlob(
            os.path.join(tmp_dir, "test_file.txt"),
            mime_type="text/plain",
            raw_text="This is a test file.",
        )
        await kfa.write_file(file_blob)

        # Verify the file was written correctly
        written_content = await kfa.read_text(file_blob.file_path)
        assert written_content == file_blob.raw_text

        # Test writing to a different path
        different_path = os.path.join(tmp_dir, "different_blob.txt")
        await kfa.write_file(file_blob, different_path)
        different_content = await kfa.read_text(different_path)
        assert different_content == file_blob.raw_text

        # 14. read_file
        read_file_blob = await kfa.read_file(file_blob.file_path)
        assert read_file_blob is not None
        assert read_file_blob.file_path == file_blob.file_path
        assert read_file_blob.mime_blob.mime_type == "text/plain"
        assert read_file_blob.mime_blob.raw_text == file_blob.raw_text

        # Test reading non-existent file
        non_existent_blob_path = os.path.join(tmp_dir, "non_existent_blob.txt")
        non_existent_blob = await kfa.read_file(non_existent_blob_path)
        assert non_existent_blob is None

        # 15. FileBlob.replace
        original_blob = kfa.FileBlob(
            "original.txt", mime_type="text/plain", raw_text="original"
        )

        # Replace file_path
        replaced_path_blob = original_blob.replace(file_path="new.txt")
        assert replaced_path_blob.file_path == "new.txt"
        assert replaced_path_blob.mime_blob.raw_text == "original"

        # Replace mime_type
        replaced_mime_blob = original_blob.replace(mime_type="text/html")
        assert replaced_mime_blob.file_path == "original.txt"
        assert replaced_mime_blob.mime_blob.mime_type == "text/html"
        assert replaced_mime_blob.mime_blob.raw_text == "original"

        # Replace raw_text
        replaced_text_blob = original_blob.replace(raw_text="new text")
        assert replaced_text_blob.file_path == "original.txt"
        assert replaced_text_blob.mime_blob.mime_type == "text/plain"
        assert replaced_text_blob.mime_blob.raw_text == "new text"

        # Replace multiple properties
        replaced_multiple_blob = original_blob.replace(
            file_path="multiple.txt",
            mime_type="application/json",
            raw_text='{"key": "value"}',
        )
        assert replaced_multiple_blob.file_path == "multiple.txt"
        assert replaced_multiple_blob.mime_blob.mime_type == "application/json"
        assert replaced_multiple_blob.mime_blob.raw_text == '{"key": "value"}'
