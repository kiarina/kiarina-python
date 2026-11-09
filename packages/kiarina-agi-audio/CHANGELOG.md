# Changelog

All notable changes to the kiarina-agi-audio package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.42.0] - 2026-11-09

### Changed
- Require google-genai 3 (`google-genai>=3.0.0,<4`) and kiarina-lib-google 2.42.0. The Google ASR and TTS providers keep the Gemini Developer API on `v1beta` (google-genai 3 defaults to `v1`).

## [2.28.0] - 2026-09-05

### Changed
- Support OpenAI Python 3.x.

## [2.15.0] - 2026-07-14

### Changed

- Replace pydub and ffprobe-dependent TTS audio processing with direct FFmpeg processing through imageio-ffmpeg.

## [2.9.0] - 2026-07-09

### Added
- Add the `kiarina-agi-audio` package.
- Add lazy default model downloads for CLAP, ECAPA-TDNN, YAMNet, Pyannote SCD, and Silero VAD.

### Changed
- Mark tests that download models or configs with `pytest.mark.downloads_model` and skip them on GitHub Actions.
- Update the CLAP default ONNX model filename, URL, and checksum to use `audio_model.onnx`.

### Fixed
- Add the Python 3.13 `audioop` compatibility dependency for TTS providers.
- Skip microphone source tests when PortAudio is unavailable.
- Avoid external credentials and missing CI assets in audio provider tests.
