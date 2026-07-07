from pathlib import Path
from unittest.mock import Mock

import pytest

from kiarina.agi.image_detection_model import ImageDetectionModelSettings
from kiarina.agi.image_detection_provider_impl.dfine import (
    DFineImageDetectionProvider,
    DFineImageDetectionProviderSettings,
)
from kiarina.agi.image_detection_provider_impl.yunet import (
    YuNetImageDetectionProvider,
    YuNetImageDetectionProviderSettings,
)
from kiarina.agi.image_embedding_model import ImageEmbeddingModelSettings
from kiarina.agi.image_embedding_provider_impl.sface import (
    SFaceImageEmbeddingProvider,
    SFaceImageEmbeddingProviderSettings,
)
from kiarina.agi.image_embedding_provider_impl.siglip2 import (
    SigLIP2ImageEmbeddingProvider,
    SigLIP2ImageEmbeddingProviderSettings,
)

Provider = (
    DFineImageDetectionProvider
    | YuNetImageDetectionProvider
    | SFaceImageEmbeddingProvider
    | SigLIP2ImageEmbeddingProvider
)


def test_builtin_presets_use_default_model_paths() -> None:
    detection = ImageDetectionModelSettings()
    embedding = ImageEmbeddingModelSettings()

    assert detection.presets["yunet"].provider_config == {}
    assert detection.presets["dfine"].provider_config == {}
    assert embedding.presets["sface"].provider_config == {}
    assert embedding.presets["siglip2"].provider_config == {}


@pytest.mark.parametrize(
    ("provider", "module", "expected_url", "expected_sha256", "expected_path"),
    [
        (
            YuNetImageDetectionProvider(
                YuNetImageDetectionProviderSettings(
                    model_url="https://example.com/yunet.onnx",
                    model_sha256="yunet-sha256",
                    model_filename="custom-yunet.onnx",
                )
            ),
            "kiarina.agi.image_detection_provider_impl.yunet._models.yunet_image_detection_provider",
            "https://example.com/yunet.onnx",
            "yunet-sha256",
            "models/yunet/custom-yunet.onnx",
        ),
        (
            SFaceImageEmbeddingProvider(
                SFaceImageEmbeddingProviderSettings(
                    model_url="https://example.com/sface.onnx",
                    model_sha256="sface-sha256",
                    model_filename="custom-sface.onnx",
                )
            ),
            "kiarina.agi.image_embedding_provider_impl.sface._models.sface_image_embedding_provider",
            "https://example.com/sface.onnx",
            "sface-sha256",
            "models/sface/custom-sface.onnx",
        ),
        (
            SigLIP2ImageEmbeddingProvider(
                SigLIP2ImageEmbeddingProviderSettings(
                    model_url="https://example.com/siglip2.onnx",
                    model_sha256="siglip2-sha256",
                    model_filename="custom-siglip2.onnx",
                )
            ),
            "kiarina.agi.image_embedding_provider_impl.siglip2._models.siglip2_image_embedding_provider",
            "https://example.com/siglip2.onnx",
            "siglip2-sha256",
            "models/siglip2/custom-siglip2.onnx",
        ),
        (
            DFineImageDetectionProvider(
                DFineImageDetectionProviderSettings(
                    model_url="https://example.com/dfine.onnx",
                    model_sha256="dfine-sha256",
                    model_filename="custom-dfine.onnx",
                )
            ),
            "kiarina.agi.image_detection_provider_impl.dfine._models.dfine_image_detection_provider",
            "https://example.com/dfine.onnx",
            "dfine-sha256",
            "models/dfine/custom-dfine.onnx",
        ),
    ],
)
def test_default_model_path_uses_cache(
    provider: Provider,
    module: str,
    expected_url: str,
    expected_sha256: str,
    expected_path: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    download_file = Mock(side_effect=lambda _url, _sha256, cache_path: cache_path)
    monkeypatch.setattr(f"{module}.download_file", download_file)
    monkeypatch.setattr(
        f"{module}.user_directory.get_user_cache_dir",
        lambda: tmp_path,
    )

    assert provider._resolve_model_path() == tmp_path / expected_path
    assert download_file.call_count == 1
    assert download_file.call_args.args[0] == expected_url
    assert download_file.call_args.args[1] == expected_sha256
    assert download_file.call_args.args[2] == tmp_path / expected_path


@pytest.mark.parametrize(
    ("provider", "module"),
    [
        (
            YuNetImageDetectionProvider(
                YuNetImageDetectionProviderSettings(model_path="~/model.onnx")
            ),
            "kiarina.agi.image_detection_provider_impl.yunet._models.yunet_image_detection_provider",
        ),
        (
            SFaceImageEmbeddingProvider(
                SFaceImageEmbeddingProviderSettings(model_path="~/model.onnx")
            ),
            "kiarina.agi.image_embedding_provider_impl.sface._models.sface_image_embedding_provider",
        ),
        (
            SigLIP2ImageEmbeddingProvider(
                SigLIP2ImageEmbeddingProviderSettings(model_path="~/model.onnx")
            ),
            "kiarina.agi.image_embedding_provider_impl.siglip2._models.siglip2_image_embedding_provider",
        ),
        (
            DFineImageDetectionProvider(
                DFineImageDetectionProviderSettings(model_path="~/model.onnx")
            ),
            "kiarina.agi.image_detection_provider_impl.dfine._models.dfine_image_detection_provider",
        ),
    ],
)
def test_explicit_model_path_does_not_use_cache(
    provider: Provider,
    module: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    download_file = Mock()
    monkeypatch.setattr(f"{module}.download_file", download_file)

    assert provider._resolve_model_path() == Path("~/model.onnx").expanduser()
    download_file.assert_not_called()


def test_dfine_resolves_default_label_map_independently(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    provider = DFineImageDetectionProvider(
        DFineImageDetectionProviderSettings(
            model_path="/custom/model.onnx",
            config_url="https://example.com/config.json",
            config_sha256="config-sha256",
            config_filename="custom-config.json",
        )
    )
    config_path = tmp_path / "models" / "dfine" / "custom-config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        '{"id2label": {"0": "person", "1": "bicycle"}}',
        encoding="utf-8",
    )
    download_file = Mock(return_value=config_path)
    monkeypatch.setattr(
        "kiarina.agi.image_detection_provider_impl.dfine._models.dfine_image_detection_provider.download_file",
        download_file,
    )
    monkeypatch.setattr(
        "kiarina.agi.image_detection_provider_impl.dfine._models.dfine_image_detection_provider.user_directory.get_user_cache_dir",
        lambda: tmp_path,
    )

    assert provider._resolve_model_path() == Path("/custom/model.onnx")
    assert provider.labels == ["person", "bicycle"]
    assert not (tmp_path / "models" / "dfine" / "coco_labels.txt").exists()
    download_file.assert_called_once()
    assert download_file.call_args.args[0] == "https://example.com/config.json"
    assert download_file.call_args.args[1] == "config-sha256"
    assert download_file.call_args.args[2] == config_path


def test_dfine_explicit_label_map_does_not_use_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = DFineImageDetectionProvider(
        DFineImageDetectionProviderSettings(label_map_path="~/labels.txt")
    )
    download_file = Mock()
    monkeypatch.setattr(
        "kiarina.agi.image_detection_provider_impl.dfine._models.dfine_image_detection_provider.download_file",
        download_file,
    )

    assert provider._resolve_label_map_path() == Path("~/labels.txt").expanduser()
    download_file.assert_not_called()


def test_download_metadata_can_be_overridden_by_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "KIARINA_AGI_IMAGE_DETECTION_PROVIDER_IMPL_YUNET_MODEL_URL",
        "https://example.com/env-yunet.onnx",
    )
    monkeypatch.setenv(
        "KIARINA_AGI_IMAGE_DETECTION_PROVIDER_IMPL_YUNET_MODEL_SHA256",
        "env-yunet-sha256",
    )
    monkeypatch.setenv(
        "KIARINA_AGI_IMAGE_DETECTION_PROVIDER_IMPL_YUNET_MODEL_FILENAME",
        "env-yunet.onnx",
    )

    settings = YuNetImageDetectionProviderSettings()

    assert settings.model_url == "https://example.com/env-yunet.onnx"
    assert settings.model_sha256 == "env-yunet-sha256"
    assert settings.model_filename == "env-yunet.onnx"
