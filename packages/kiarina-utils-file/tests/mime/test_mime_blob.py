from kiarina.utils.mime import MIMEBlob


def test_mime_blob_comprehensive():
    """Comprehensive test for MIMEBlob class"""

    data = MIMEBlob(mime_type="text/plain", raw_text="Hello, World!")
    assert data.mime_type == "text/plain"
    assert data.raw_data == b"Hello, World!"
    assert data.raw_text == "Hello, World!"
    assert len(data.raw_base64_str) > 0
    assert len(data.raw_base64_url) > 0
    assert len(data.hash_string) > 0
    assert data.ext == ".txt"
    assert data.hashed_file_name.endswith(".txt")
    assert data.is_binary() is False
    assert data.is_text() is True
    assert data.__dict__.get("raw_text") is not None
    assert data.__dict__.get("raw_base64_str") is not None
    assert data.__dict__.get("hash_string") is not None
    assert data.__dict__.get("ext") is not None
