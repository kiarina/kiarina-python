from kiarina.agi.ocr_provider_impl.mock import (
    MockOCRProvider,
    create_mock_ocr_provider,
)


def test_create_mock_ocr_provider() -> None:
    provider = create_mock_ocr_provider()
    assert isinstance(provider, MockOCRProvider)
