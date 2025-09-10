import kiarina.utils.mime as km


def test_create_mime_blob(data_dir):
    with open(data_dir / "small" / "apple_1024x1024_138kb.jpg", "rb") as f:
        raw_data = f.read()

    mime_blob = km.create_mime_blob(raw_data=raw_data)
    assert mime_blob.mime_type == "image/jpeg"
    assert mime_blob.raw_data == raw_data
