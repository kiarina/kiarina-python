---
title: About kiarina-utils-file package
description: >-
  kiarina-utils-file is a comprehensive library for file I/O operations
  with automatic encoding detection, MIME type detection, and support for various file formats.
---

kiarina-utils-file provides comprehensive file I/O operations with smart detection capabilities and support for multiple file formats.
This package is designed for production use with features like atomic operations, thread safety, and both sync/async APIs.

Key features include:
- Multiple file formats support (text, binary, JSON, YAML, Markdown)
- Sync & Async API support for high-performance applications
- Atomic operations with file locking for safe concurrent access
- Automatic encoding detection with nkf support
- MIME type detection using multiple detection methods
- Extension handling for complex multi-part extensions (.tar.gz, .tar.gz.gpg)
- FileBlob and MIMEBlob data containers with metadata
- Hash-based naming for content-addressable storage
- Error handling with configurable defaults
- Type safety with full type hints

Main modules:
- `kiarina.utils.file`: Synchronous file operations
- `kiarina.utils.file.asyncio`: Asynchronous file operations
- `kiarina.utils.mime`: MIME type detection and handling
- `kiarina.utils.ext`: Extension detection and extraction
- `kiarina.utils.encoding`: Encoding detection and conversion
