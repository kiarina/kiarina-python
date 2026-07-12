import pytest

from kiarina.agi.ocr_provider_impl.rapidocr import (
    RapidOCRProvider,
    create_rapidocr_provider,
)

pytestmark = [pytest.mark.downloads_model]


def test_create_rapidocr_provider() -> None:
    provider = create_rapidocr_provider()
    assert isinstance(provider, RapidOCRProvider)
