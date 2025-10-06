---
title: File Placement for pytest
description: >-
  When using files with pytest,
  place them under tests/fixtures/, tests/data/small/, or tests/data/large/.
  Large files are downloaded using `mise run download-test-data`.
---

When using files with pytest, the placement location varies depending on the nature of the file.

- `tests/fixtures/`
  - Files such as JSON, YAML, etc. that are loaded by pytest fixtures and converted to data
- `tests/data/small/`
  - Small files of 1 MB or less
- `tests/data/large/`
  - Large files exceeding 1 MB
  - This directory is .gitignored and not managed by Git

Do not place files directly in `tests/data/large/`.
Required files should be registered in the GitHub Releases of the public repository below and downloaded for use.

- https://github.com/kiarina/test-data

Running the following command will download files to `tests/data/large/`.

```sh
mise run download-test-data
```
