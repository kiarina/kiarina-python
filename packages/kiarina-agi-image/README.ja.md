# kiarina-agi-image

[English](README.md) | 日本語

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-image.svg)](https://pypi.org/project/kiarina-agi-image/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE] What is this?
> `kiarina-agi-image` は、AI agent 向けの image detection、embedding、generation、segmentation、OCR を提供します。

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

`all` Extra は、上記の optional dependency をすべてインストールします。

## Installation

```bash
pip install kiarina-agi-image
```

すべての provider implementation を利用する場合:

```bash
pip install "kiarina-agi-image[all]"
```

## Features

- **Image Detection**
  Object と face を検出し、crop や face alignment を行います。
- **Image Embedding**
  Image embedding を生成します。
- **Image Generation**
  Google、OpenAI、kiapi、mock provider で画像を生成・編集します。
- **Image Segmentation**
  元画像と同じ解像度の二値 mask と confidence map を生成します。
- **OCR**
  RGB image から文字列、信頼度、正規化された polygon を取得します。

### Image Segmentation with BiRefNet

BiRefNet provider は、RGB image から前景を segmentation します。入力は `[height, width, 3]`、`uint8` の RGB image です。

```python
from kiarina.agi.image_segmentation_model import segment_image

result = await segment_image(pixels, run_context=run_context)
```

`result.mask` は元画像と同じ `[height, width]`、`uint8` で、値は `0` または `255` です。`result.confidence_map` は同じ shape の `float32` で、値は `0.0` から `1.0` です。

File から背景を削除した透過画像を作る場合は、`remove_background` を使用します。出力は PNG または WebP の `MIMEBlob` です。

```python
from kiarina.agi.image_segmentation_model import remove_background

mime_blob = await remove_background(
    "input.jpg",
    output_format="png",
    run_context=run_context,
)
```

### OCR with RapidOCR

RapidOCR provider は ONNX Runtime CPU 上で PP-OCRv6-small の文字検出と日本語文字認識を実行します。入力は `[height, width, 3]`、`uint8` の RGB image です。

```python
from kiarina.agi.ocr_model import ocr_image

results = await ocr_image(pixels, run_context=run_context)

for result in results:
    print(result.text, result.score, result.polygon)
```

`polygon` は元画像を基準に `0.0` から `1.0` へ正規化された4点です。

### Image Generation through kiapi

`kiapi` model alias は、既定で `http://localhost:8000` の kiapi と `qwen` family を使用します。`family` は `flux2`、`qwen`、`ernie` から選択でき、family 固有の request parameter は `extra_params` に指定します。

```python
from kiarina.agi.image_generation_model import generate_image

result = await generate_image(
    "A cafe sign that reads KIARINA",
    image_generation_options={
        "image_generation_model": "kiapi?family=flux2&extra_params.width=512&extra_params.height=512"
    },
)
```

`file_paths` を指定すると、file を kiapi に upload し、選択した family の edit endpoint に渡します。`ernie` は入力画像を 1 枚だけ受け取ります。

### Model Cache

YuNet、D-FINE、SFace、SigLIP2、BiRefNet は、`model_path` が `None` の場合、初回利用時に既定モデルをダウンロードします。D-FINE は、`label_map_path` が `None` の場合、検証済みの `config.json` をダウンロードし、そこから既定ラベルを生成します。

ファイルは `user_directory.get_user_cache_dir() / "models" / <implementation>` にキャッシュされます。明示したパスは常に優先され、その場合は対応するファイルをダウンロードしません。

既定の download URL、SHA-256 digest、cache filename は provider settings であり、settings、環境変数、config で上書きできます。取得元を変える場合、既存 cache を再利用したくないときは filename も変更してください。

## API Reference

### `kiarina.agi.image_detection_model`

Image detection model の設定、registry、検出・crop helper を公開します。

### `kiarina.agi.image_detection_provider`

Image detection provider protocol、base class、検出結果 view、registry を公開します。

### `kiarina.agi.image_embedding_model`

Image embedding model の設定、registry、embedding helper を公開します。

### `kiarina.agi.image_embedding_provider`

Image embedding provider protocol、base class、registry を公開します。

### `kiarina.agi.image_generation_model`

Image generation model の設定、registry、generation helper を公開します。

### `kiarina.agi.image_generation_provider`

Image generation provider protocol、base class、result view、registry を公開します。

Provider implementation は、対応する `kiarina.agi.*_provider_impl.<name>` から import します。

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

`image_segmentation_model_registry` は image segmentation model の registry、`settings_manager` は `ImageSegmentationModelSettings` の settings manager です。

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

`image_segmentation_provider_registry` は image segmentation provider の registry、`settings_manager` は `ImageSegmentationProviderSettings` の settings manager です。

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

各 implementation の `settings_manager` は、対応する settings を管理します。

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

管理された settings から provider を作成し、keyword argument を上書きとして適用します。

#### `KiapiImageGenerationProvider`

```python
class KiapiImageGenerationProvider(BaseImageGenerationProvider):
    def __init__(self, settings: KiapiImageGenerationProviderSettings) -> None: ...
```

kiapi の `flux2`、`qwen`、`ernie` family で画像を生成・編集します。

#### `KiapiImageGenerationProviderSettings`

```python
class KiapiImageGenerationProviderSettings(BaseSettings):
    kiapi_base_url: str = "http://localhost:8000"
    family: Literal["flux2", "qwen", "ernie"] = "qwen"
    timeout: float = 1800.0
    extra_params: dict[str, Any] = {}
```

`settings_manager` は、この settings 用の `SettingsManager` instance です。

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

`ocr_model_registry` は OCR model の registry、`settings_manager` は `OCRModelSettings` の settings manager です。

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

`ocr_provider_registry` は OCR provider の registry、`settings_manager` は `OCRProviderSettings` の settings manager です。

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
