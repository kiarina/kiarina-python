# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING**: Changed MIME type detection strategy to prioritize file extensions over content analysis
  - `detect_mime_type()` now prioritizes extension-based detection (custom dictionary → mimetypes) before falling back to content analysis (puremagic)
  - **Philosophy**: File extensions represent explicit user intent and should be trusted
  - **Rationale**: More intuitive behavior for applications - `.md` files are treated as Markdown even if content looks like plain text
  - **Migration**: If your code relies on content-based detection taking precedence, you may need to adjust expectations
  - Reordered function arguments: `file_name_hint` is now the first parameter (before `raw_data` and `stream`)
  - Updated all docstrings and module documentation to reflect the new detection strategy
- Improved `detect_mime_type()` API to reduce cognitive load
  - Introduced `MimeDetectionOptions` TypedDict to group optional parameters
  - Replaced multiple individual parameters with a single `options` parameter
  - All detection options (mime_aliases, custom_mime_types, multi_extensions, etc.) are now passed through the `options` dictionary
  - Maintains backward compatibility through optional parameter design
  - Added comprehensive docstring examples for the new API

### Fixed
- Fixed symbolic link handling in `read_binary()` and `write_binary()` operations
  - Symlinks are now properly resolved to their target files using `os.path.realpath()`
  - Write operations through symlinks no longer replace the symlink with a regular file
  - File locks are now correctly applied to the actual target file, not the symlink itself
  - Added comprehensive tests for symlink operations including broken symlinks

## [1.2.0] - 2025-09-25

### Changed
- No changes

## [1.1.1] - 2025-09-11

### Changed
- No changes

## [1.1.0] - 2025-09-11

### Changed
- No changes

## [1.0.1] - 2025-09-11

### Fixed
- Fixed file permission preservation issue in `write_binary()` operations
  - Existing file permissions (mode, uid, gid) are now properly preserved when updating files
  - Added `_preserve_permissions()` function to maintain original file access controls
  - Implemented permission preservation for both sync and async write operations
  - Added comprehensive tests for permission preservation functionality
  - Improved security by preventing unintended permission changes during file updates

## [1.0.0] - 2025-09-09

### Added
- Initial release of kiarina-utils-file
- Comprehensive file I/O operations with sync and async support
- Automatic encoding detection with nkf support for Japanese text
- MIME type detection using multiple detection methods (puremagic, custom dictionary, mimetypes)
- Support for complex multi-part file extensions (.tar.gz, .tar.gz.gpg)
- FileBlob and MIMEBlob data containers with metadata and format conversion
- Atomic file operations with temporary files and file locking
- Thread-safe file operations with automatic lock cleanup
- Support for multiple file formats: text, binary, JSON, YAML
- Hash-based content addressing for file naming
- Configurable behavior through environment variables
- Comprehensive test suite with 100% coverage
- Full type hints and mypy compatibility
- Performance optimizations with lazy loading and caching

### File Operations
- `read_file()` and `write_file()` for high-level FileBlob operations
- `read_text()` and `write_text()` with automatic encoding detection
- `read_binary()` and `write_binary()` for raw data operations
- `read_json_dict()`, `write_json_dict()`, `read_json_list()`, `write_json_list()` for JSON
- `read_yaml_dict()`, `write_yaml_dict()`, `read_yaml_list()`, `write_yaml_list()` for YAML
- `remove_file()` for safe file deletion
- Full async equivalents in `kiarina.utils.file.asyncio` module

### Encoding Detection (`kiarina.utils.encoding`)
- `detect_encoding()` with charset_normalizer, nkf, and fallback detection
- `decode_binary_to_text()` with automatic encoding detection and newline normalization
- `is_binary()` for binary vs text classification
- `normalize_newlines()` for universal newline handling
- `get_default_encoding()` for configuration access
- Configurable nkf usage with automatic Japanese environment detection
- Support for fallback encoding lists and confidence thresholds

### MIME Type Detection (`kiarina.utils.mime`)
- `detect_mime_type()` with multi-stage detection strategy
- `create_mime_blob()` for automatic MIME blob creation
- `apply_mime_alias()` for MIME type normalization
- MIMEBlob class with format conversion and hash-based naming
- Support for content-based detection (puremagic) and extension-based fallback
- Configurable MIME type aliases and custom type mappings

### Extension Detection (`kiarina.utils.ext`)
- `detect_extension()` for MIME type to extension conversion
- `extract_extension()` with multi-part extension support
- Support for complex extensions like .tar.gz, .tar.gz.gpg
- Configurable extension dictionaries and multi-part patterns
- URL parameter and fragment cleaning

### Data Containers
- FileBlob: File data with path information and MIME type detection
- MIMEBlob: MIME-typed binary data with format conversion
- Support for text, Base64, and data URL representations
- Hash-based file naming with configurable algorithms
- Immutable design with `replace()` methods for updates

### Configuration
- Environment variable configuration for all modules
- Settings managers with pydantic-settings-manager integration
- Configurable lock directories and cleanup behavior
- Customizable detection thresholds and algorithms
- Support for custom MIME types and extension mappings

### Performance Features
- Lazy property evaluation with caching
- Efficient sampling for large file detection
- Non-blocking async I/O operations
- Atomic file operations with minimal overhead
- Automatic cleanup of temporary files and locks
- Memory-efficient processing of large files

### Dependencies
- aiofiles>=24.1.0 - Async file operations
- charset-normalizer>=3.4.3 - Encoding detection
- filelock>=3.19.1 - File locking
- pydantic>=2.11.7 - Data validation
- pydantic-settings>=2.10.1 - Settings management
- pydantic-settings-manager>=2.1.0 - Advanced settings management
- pyyaml>=6.0.2 - YAML support

### Optional Dependencies
- puremagic>=1.30 - Enhanced MIME type detection from file content
