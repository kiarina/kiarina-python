# kiarina-agi-image

English | [日本語](README.ja.md)

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-image.svg)](https://pypi.org/project/kiarina-agi-image/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE] What is this?
> `kiarina-agi-image` provides image detection, embedding, generation, segmentation, and OCR for AI agents.

## Dependencies

### Required Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-base](../kiarina-agi-base/) | `>=2.7.0` | MIT |
| [kiarina-agi-data](../kiarina-agi-data/) | `>=2.7.0` | MIT |
| [kiarina-agi-file](../kiarina-agi-file/) | `>=2.6.0` | MIT |
| [kiarina-utils-app](../kiarina-utils-app/) | `>=2.4.0` | MIT |
| [kiarina-utils-common](../kiarina-utils-common/) | `>=2.3.0` | MIT |
| [kiarina-utils-file](../kiarina-utils-file/) | `>=2.3.1` | MIT |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0,<3` | BSD-3-Clause |
| [OpenCV](https://github.com/opencv/opencv-python) | `>=4.12.0,<5` | Apache-2.0 |
| [Pillow](https://github.com/python-pillow/Pillow) | `>=11.3.0,<12` | HPND |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7,<3` | MIT |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1,<3` | MIT |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | MIT |

### Optional Dependencies

| Package | Extras |
| --- | --- |
| google-genai | `image-embedding-provider-gemini`<br>`image-generation-provider-google` |
| httpx | `image-embedding-provider-qwen3-vl`<br>`image-generation-provider-kiapi`<br>`image-generation-provider-openai` |
| kiarina-lib-google | `image-embedding-provider-gemini`<br>`image-generation-provider-google` |
| kiarina-lib-openai | `image-generation-provider-openai` |
| onnxruntime | `image-detection-provider-dfine`<br>`image-embedding-provider-siglip2`<br>`image-segmentation-provider-birefnet`<br>`ocr-provider-rapidocr` |
| openai | `image-generation-provider-openai` |
| rapidocr | `ocr-provider-rapidocr` |

The `all` Extra installs every optional dependency listed above.

## Installation

```bash
pip install kiarina-agi-image
```

To use every provider implementation:

```bash
pip install "kiarina-agi-image[all]"
```

## Features

- **Image Detection**
  Detect objects and faces, crop objects, and align faces.
- **Image Embedding**
  Create image embeddings.
- **Image Generation**
  Generate and edit images with Google, OpenAI, kiapi, and mock providers.
- **Image Segmentation**
  Create binary masks and confidence maps at the source image resolution.
- **OCR**
  Extract text, confidence scores, and normalized polygons from RGB images.

### Image Segmentation with BiRefNet

The BiRefNet provider segments the foreground of an RGB image. Input images must be RGB arrays shaped as `[height, width, 3]` with `uint8` values.

```python
from kiarina.agi.image_segmentation_model import segment_image

result = await segment_image(pixels, run_context=run_context)
```

`result.mask` is a `uint8` array shaped as `[height, width]` at the source image resolution and contains only `0` or `255`. `result.confidence_map` is a `float32` array with the same shape and values from `0.0` to `1.0`.

Use `remove_background` to create a transparent image from a file. It returns a PNG or WebP `MIMEBlob`.

```python
from kiarina.agi.image_segmentation_model import remove_background

mime_blob = await remove_background(
    "input.jpg",
    output_format="png",
    run_context=run_context,
)
```

### OCR with RapidOCR

The RapidOCR provider runs PP-OCRv6-small text detection and Japanese text recognition on ONNX Runtime CPU. Input images must be RGB arrays shaped as `[height, width, 3]` with `uint8` values.

```python
from kiarina.agi.ocr_model import ocr_image

results = await ocr_image(pixels, run_context=run_context)

for result in results:
    print(result.text, result.score, result.polygon)
```

Each `polygon` contains four points normalized from `0.0` to `1.0` against the source image.

### Image Generation through kiapi

The `kiapi` model alias uses kiapi at `http://localhost:8000` and the `qwen` family by default. Select `flux2`, `qwen`, or `ernie` with `family`, and pass family-specific request parameters in `extra_params`.

```python
from kiarina.agi.image_generation_model import generate_image

result = await generate_image(
    "A cafe sign that reads KIARINA",
    image_generation_options={
        "image_generation_model": "kiapi?family=flux2&extra_params.width=512&extra_params.height=512"
    },
)
```

When `file_paths` are supplied, the files are uploaded to kiapi and passed to the selected family's edit endpoint. The `ernie` family accepts one input image.

### Model Cache

YuNet, D-FINE, SFace, SigLIP2, and BiRefNet download their default model on first use when `model_path` is `None`. D-FINE also downloads a verified `config.json` and generates default labels from it when `label_map_path` is `None`.

Files are cached under `user_directory.get_user_cache_dir() / "models" / <implementation>`. An explicit path always takes precedence and prevents downloading the corresponding file.

The default download URL, SHA-256 digest, and cache filename are provider settings and can be overridden through settings, environment variables, or config. When changing the source, also change the filename if an existing cached file should not be reused.

## API Reference

### `kiarina.agi.image_detection_model`

Exports image detection model settings, registries, detection helpers, and cropping helpers.

### `kiarina.agi.image_detection_provider`

Exports the image detection provider protocol, base class, detection result view, and registry.

### `kiarina.agi.image_embedding_model`

Exports image embedding model settings, registry, and embedding helper.

### `kiarina.agi.image_embedding_provider`

Exports the image embedding provider protocol, base class, and registry.

### `kiarina.agi.image_generation_model`

Exports image generation model settings, registry, and generation helper.

### `kiarina.agi.image_generation_provider`

Exports the image generation provider protocol, base class, result view, and registry.

Import provider implementations from the matching `kiarina.agi.*_provider_impl.<name>` path.

### `kiarina.agi.image_segmentation_model`

```python
async def remove_background(
    file_path: str,
    *,
    output_format: Literal["png", "webp"] = "png",
    image_segmentation_options: ImageSegmentationOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> MIMEBlob: ...

async def segment_image(
    pixels: ImagePixels,
    *,
    image_segmentation_options: ImageSegmentationOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> ImageSegmentationResult: ...

class ImageSegmentationModel:
    def __init__(
        self,
        name: ImageSegmentationModelName,
        config: ImageSegmentationModelConfig,
    ) -> None: ...
    @property
    def provider_name(self) -> ImageSegmentationProviderName: ...
    @property
    def provider_config(self) -> dict[str, Any]: ...
    @property
    def provider(self) -> ImageSegmentationProvider: ...
    async def segment(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> ImageSegmentationResult: ...

class ImageSegmentationModelConfig(BaseModel):
    provider_name: ImageSegmentationProviderName
    provider_config: dict[str, Any] = {}
    visible: bool = True

class ImageSegmentationModelSettings(BaseSettings):
    default: ImageSegmentationModelSpecifier = "birefnet"
    aliases: dict[ImageSegmentationModelAlias, ImageSegmentationModelName]
    presets: dict[ImageSegmentationModelName, ImageSegmentationModelConfig]
    customs: dict[ImageSegmentationModelName, ImageSegmentationModelConfig]

class ImageSegmentationOptions(TypedDict, total=False):
    image_segmentation_model: (
        ImageSegmentationModel | ImageSegmentationModelSpecifier | None
    )

ImageSegmentationModelAlias: TypeAlias = str
ImageSegmentationModelName: TypeAlias = str
ImageSegmentationModelSpecifier: TypeAlias = str
```

`image_segmentation_model_registry` is the image segmentation model registry. `settings_manager` manages `ImageSegmentationModelSettings`.

### `kiarina.agi.image_segmentation_provider`

```python
class ImageSegmentationProvider(Protocol):
    name: ImageSegmentationProviderName
    async def segment(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> ImageSegmentationResult: ...

class BaseImageSegmentationProvider(ImageSegmentationProvider, ABC):
    def __init__(self) -> None: ...

class ImageSegmentationProviderSettings(BaseSettings):
    presets: dict[ImageSegmentationProviderName, ImportPath]
    customs: dict[ImageSegmentationProviderName, ImportPath]

@dataclass
class ImageSegmentationResult:
    mask: ImageSegmentationMask
    confidence_map: ImageSegmentationConfidenceMap | None = None

ImageSegmentationConfidenceMap: TypeAlias = NDArray[np.float32]
ImageSegmentationMask: TypeAlias = NDArray[np.uint8]
ImageSegmentationProviderName: TypeAlias = str
```

`image_segmentation_provider_registry` is the image segmentation provider registry. `settings_manager` manages `ImageSegmentationProviderSettings`.

### `kiarina.agi.image_segmentation_provider_impl.mock`

```python
def create_mock_image_segmentation_provider(
    **kwargs: Any,
) -> MockImageSegmentationProvider: ...

class MockImageSegmentationProvider(BaseImageSegmentationProvider):
    def __init__(self, settings: MockImageSegmentationProviderSettings) -> None: ...

class MockImageSegmentationProviderSettings(BaseSettings):
    mask_value: Literal[0, 255] = 255
    confidence: float | None = None
```

### `kiarina.agi.image_segmentation_provider_impl.birefnet`

```python
def create_birefnet_image_segmentation_provider(
    **kwargs: Any,
) -> BiRefNetImageSegmentationProvider: ...

class BiRefNetImageSegmentationProvider(BaseImageSegmentationProvider):
    def __init__(
        self,
        settings: BiRefNetImageSegmentationProviderSettings,
    ) -> None: ...
    @property
    def session(self) -> InferenceSession: ...

class BiRefNetImageSegmentationProviderSettings(BaseSettings):
    model_path: str | Path | None = None
    model_url: str
    model_sha256: str
    model_filename: str
    input_size: int = 1024
    threshold: float = 0.5
    image_mean: list[float]
    image_std: list[float]
    image_input_name: str = "input_image"
    output_name: str = "output_image"
    execution_providers: list[str] = ["CPUExecutionProvider"]
```

Each implementation exposes a `settings_manager` for its settings.

### `kiarina.agi.image_generation_provider_impl.kiapi`

```python
from kiarina.agi.image_generation_provider_impl.kiapi import (
    KiapiImageGenerationProvider,
    KiapiImageGenerationProviderSettings,
    create_kiapi_image_generation_provider,
    settings_manager,
)
```

#### `create_kiapi_image_generation_provider`

```python
def create_kiapi_image_generation_provider(
    **kwargs: Any,
) -> KiapiImageGenerationProvider: ...
```

Creates a provider from managed settings, with keyword arguments applied as overrides.

#### `KiapiImageGenerationProvider`

```python
class KiapiImageGenerationProvider(BaseImageGenerationProvider):
    def __init__(self, settings: KiapiImageGenerationProviderSettings) -> None: ...
```

Generates and edits images with the kiapi `flux2`, `qwen`, and `ernie` families.

#### `KiapiImageGenerationProviderSettings`

```python
class KiapiImageGenerationProviderSettings(BaseSettings):
    kiapi_base_url: str = "http://localhost:8000"
    family: Literal["flux2", "qwen", "ernie"] = "qwen"
    timeout: float = 1800.0
    extra_params: dict[str, Any] = {}
```

`settings_manager` is the `SettingsManager` instance for these settings.

### `kiarina.agi.ocr_model`

```python
async def ocr_image(
    pixels: ImagePixels,
    *,
    ocr_options: OCROptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> list[OCRResult]: ...

class OCRModel:
    def __init__(self, name: OCRModelName, config: OCRModelConfig) -> None: ...
    @property
    def provider_name(self) -> OCRProviderName: ...
    @property
    def provider_config(self) -> dict[str, Any]: ...
    @property
    def provider(self) -> OCRProvider: ...
    async def ocr(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[OCRResult]: ...

class OCRModelConfig(BaseModel):
    provider_name: OCRProviderName
    provider_config: dict[str, Any] = {}
    visible: bool = True

class OCRModelSettings(BaseSettings):
    default: OCRModelSpecifier = "rapidocr"
    aliases: dict[OCRModelAlias, OCRModelName]
    presets: dict[OCRModelName, OCRModelConfig]
    customs: dict[OCRModelName, OCRModelConfig]

class OCROptions(TypedDict, total=False):
    ocr_model: OCRModel | OCRModelSpecifier | None

OCRModelAlias: TypeAlias = str
OCRModelName: TypeAlias = str
OCRModelSpecifier: TypeAlias = str
```

`ocr_model_registry` is the OCR model registry. `settings_manager` manages `OCRModelSettings`.

### `kiarina.agi.ocr_provider`

```python
class OCRProvider(Protocol):
    name: OCRProviderName
    async def ocr(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[OCRResult]: ...

class BaseOCRProvider(OCRProvider, ABC):
    def __init__(self) -> None: ...

class OCRProviderSettings(BaseSettings):
    presets: dict[OCRProviderName, ImportPath]
    customs: dict[OCRProviderName, ImportPath]

@dataclass
class OCRResult:
    text: str
    score: float
    polygon: list[list[float]]

OCRProviderName: TypeAlias = str
```

`ocr_provider_registry` is the OCR provider registry. `settings_manager` manages `OCRProviderSettings`.

### `kiarina.agi.ocr_provider_impl.mock`

```python
def create_mock_ocr_provider(**kwargs: Any) -> MockOCRProvider: ...

class MockOCRProvider(BaseOCRProvider):
    def __init__(self, settings: MockOCRProviderSettings) -> None: ...

class MockOCRProviderSettings(BaseSettings):
    results: list[OCRResult]
```

### `kiarina.agi.ocr_provider_impl.rapidocr`

```python
def create_rapidocr_provider(**kwargs: Any) -> RapidOCRProvider: ...

class RapidOCRProvider(BaseOCRProvider):
    def __init__(self, settings: RapidOCRProviderSettings) -> None: ...
    @property
    def engine(self) -> Any: ...

class RapidOCRProviderSettings(BaseSettings):
    text_score: float = 0.5
    box_threshold: float = 0.5
```
