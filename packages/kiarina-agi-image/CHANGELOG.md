# Changelog

All notable changes to the kiarina-agi-image package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.42.0] - 2026-11-09

### Changed
- Require google-genai 3 (`google-genai>=3.0.0,<4`) and kiarina-lib-google 2.42.0. The Google image embedding and image generation providers keep the Gemini Developer API on `v1beta` (google-genai 3 defaults to `v1`).

## [2.40.0] - 2026-11-07

### Changed (BREAKING)
- `opencv-python` is no longer a required dependency. It moves to the extras of the implementations that use it: `image-detection-provider-dfine`, `image-detection-provider-yunet`, `image-embedding-provider-qwen3-vl`, `image-embedding-provider-sface`, `image-embedding-provider-siglip2`, `image-segmentation-provider-birefnet`, and `all`. `crop_align_faces` imports it when called and points to `image-embedding-provider-sface` (its aligned faces are SFace's input). `BiRefNetImageSegmentationProvider` imports it with onnxruntime, with the same install hint.

## [2.37.0] - 2026-11-06

### Removed
- Remove the kiapi `ernie` family, which kiapi no longer provides.

## [2.28.0] - 2026-09-05

### Changed
- Support OpenAI Python 3.x and OpenCV Python 5.x.

## [2.21.1] - 2026-08-10

### Changed
- Require Pillow 12.3.0 or later for security fixes.

## [2.17.0] - 2026-07-26

### Changed
- Remove an obsolete RapidOCR typing suppression.

## [2.15.0] - 2026-07-14

### Added
- Add a kiapi image generation provider with Flux2, Qwen, and ERNIE families.
- Add image segmentation APIs with mock and BiRefNet ONNX providers.
- Add a file-based background removal helper with PNG and WebP output.
- Add OCR model and provider APIs with mock and RapidOCR implementations.

## [2.9.0] - 2026-07-09

### Changed
- Mark local model download tests explicitly and skip them on GitHub Actions.

## [2.8.0] - 2026-07-08

### Added
- Add the `kiarina-agi-image` package.
- Add lazy default model downloads for YuNet, D-FINE, SFace, and SigLIP2.
- Add configurable default download metadata for local image providers.

### Changed
- Add concrete type annotations to package tests and remove mypy suppressions.
- Add explicit costly image test shortcuts and VS Code pytest settings.
- Use user cache model downloads in real local provider tests.
- Use `kiarina-lib-google` to resolve Google Gen AI client options for Gemini embedding and Google image generation providers.

## [2.7.0] - 2026-07-06

### Added
- Add image detection, embedding, and generation APIs.
- Add optional D-FINE, Gemini, Google, OpenAI, Qwen3-VL, SFace, SigLIP2, and YuNet implementations.
