# Changelog

All notable changes to the kiarina-agi-data-builder package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.32.0] - 2026-09-20

### Changed (BREAKING)

- Resolve file segment normalizers through a `ComponentRegistry`. `file_segment_normalizer_registry` replaces `create_file_segment_normalizer`, which is removed, and the `FileSegmentNormalizerSettings.normalizers` setting is renamed to `customs`. Normalizers can now be registered at runtime and selected with a `{name}?{config}` specifier.

## [2.21.1] - 2026-08-10

### Changed

- Require Pillow 12.3.0 or later for security fixes.

## [2.19.0] - 2026-07-27

### Added

- Add capability-aware video analysis bundles with video, timestamped frames, transcripts, and ambient events.
- Add capability-aware PDF analysis bundles with PDF documents, page images, and extracted text.

## [2.15.0] - 2026-07-14

### Changed

- Replace MoviePy video processing with direct FFmpeg processing through imageio-ffmpeg.

## [2.13.0] - 2026-07-10

### Added

- Add the kiarina-agi-data-builder package.
