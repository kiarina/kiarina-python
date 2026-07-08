# Changelog

All notable changes to the kiarina-agi-audio package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Add the `kiarina-agi-audio` package.
- Add lazy default model downloads for CLAP, ECAPA-TDNN, YAMNet, Pyannote SCD, and Silero VAD.

### Changed
- Mark tests that download models or configs with `pytest.mark.downloads_model` and skip them on GitHub Actions.
- Update the CLAP default ONNX model filename, URL, and checksum to use `audio_model.onnx`.
