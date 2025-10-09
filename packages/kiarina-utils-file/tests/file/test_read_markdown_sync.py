import os
import tempfile

import pytest

import kiarina.utils.file as kf


def test_read_markdown_with_front_matter():
    """Test reading Markdown file with YAML front matter"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a Markdown file with front matter
        md_path = os.path.join(tmp_dir, "test.md")
        content = """---
title: Test Document
author: John Doe
date: 2025-01-01
tags:
  - test
  - markdown
---

# Hello World

This is a test document.
"""
        kf.write_text(md_path, content)

        # Read the Markdown file
        result = kf.read_markdown(md_path)

        assert result is not None
        assert result.metadata["title"] == "Test Document"
        assert result.metadata["author"] == "John Doe"
        # YAML parses dates as datetime.date objects
        assert str(result.metadata["date"]) == "2025-01-01"
        assert result.metadata["tags"] == ["test", "markdown"]
        assert result.content == "# Hello World\n\nThis is a test document.\n"


def test_read_markdown_without_front_matter():
    """Test reading Markdown file without front matter"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "test.md")
        content = "# Hello World\n\nThis is a test document.\n"
        kf.write_text(md_path, content)

        result = kf.read_markdown(md_path)

        assert result is not None
        assert result.metadata == {}
        assert result.content == content


def test_read_markdown_with_invalid_front_matter():
    """Test reading Markdown file with invalid YAML front matter"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "test.md")
        # Invalid YAML (missing colon)
        content = """---
title Test Document
author: John Doe
---

# Hello World
"""
        kf.write_text(md_path, content)

        result = kf.read_markdown(md_path)

        assert result is not None
        # Invalid YAML should be treated as regular content
        assert result.metadata == {}
        assert result.content == content


def test_read_markdown_with_non_dict_front_matter():
    """Test reading Markdown file with non-dict YAML front matter"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "test.md")
        # YAML that parses to a list, not a dict
        content = """---
- item1
- item2
---

# Hello World
"""
        kf.write_text(md_path, content)

        result = kf.read_markdown(md_path)

        assert result is not None
        # Non-dict YAML should be treated as regular content
        assert result.metadata == {}
        assert result.content == content


def test_read_markdown_with_non_string_keys():
    """Test reading Markdown file with non-string keys in front matter"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "test.md")
        # YAML with numeric keys
        content = """---
1: value1
2: value2
---

# Hello World
"""
        kf.write_text(md_path, content)

        result = kf.read_markdown(md_path)

        assert result is not None
        # Non-string keys should be treated as regular content
        assert result.metadata == {}
        assert result.content == content


def test_read_markdown_non_existent_file():
    """Test reading non-existent Markdown file"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "non_existent.md")

        result = kf.read_markdown(md_path)
        assert result is None


def test_read_markdown_with_default():
    """Test reading non-existent Markdown file with default value"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "non_existent.md")

        default = kf.MarkdownContent(content="Default content", metadata={})
        result = kf.read_markdown(md_path, default=default)

        assert result is not None
        assert result.content == "Default content"
        assert result.metadata == {}


def test_read_markdown_empty_file():
    """Test reading empty Markdown file"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "empty.md")
        kf.write_text(md_path, "")

        result = kf.read_markdown(md_path)

        assert result is not None
        assert result.content == ""
        assert result.metadata == {}


def test_read_markdown_only_front_matter():
    """Test reading Markdown file with only front matter"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "test.md")
        content = """---
title: Only Front Matter
---
"""
        kf.write_text(md_path, content)

        result = kf.read_markdown(md_path)

        assert result is not None
        assert result.metadata["title"] == "Only Front Matter"
        assert result.content == ""


def test_read_markdown_with_empty_front_matter():
    """Test reading Markdown file with empty front matter"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "test.md")
        content = """---
---

# Hello World
"""
        kf.write_text(md_path, content)

        result = kf.read_markdown(md_path)

        assert result is not None
        # Empty front matter (no content between ---) is treated as regular content
        assert result.metadata == {}
        assert result.content == content


def test_read_markdown_with_complex_metadata():
    """Test reading Markdown file with complex nested metadata"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "test.md")
        content = """---
title: Complex Document
author:
  name: John Doe
  email: john@example.com
tags:
  - python
  - markdown
settings:
  draft: false
  published: true
---

# Content
"""
        kf.write_text(md_path, content)

        result = kf.read_markdown(md_path)

        assert result is not None
        assert result.metadata["title"] == "Complex Document"
        assert result.metadata["author"]["name"] == "John Doe"
        assert result.metadata["author"]["email"] == "john@example.com"
        assert result.metadata["tags"] == ["python", "markdown"]
        assert result.metadata["settings"]["draft"] is False
        assert result.metadata["settings"]["published"] is True
        assert result.content == "# Content\n"


def test_markdown_content_namedtuple():
    """Test MarkdownContent as a NamedTuple"""
    content = kf.MarkdownContent(content="# Hello", metadata={"title": "Test"})

    # Test named tuple properties
    assert content.content == "# Hello"
    assert content.metadata == {"title": "Test"}

    # Test tuple unpacking
    text, meta = content
    assert text == "# Hello"
    assert meta == {"title": "Test"}

    # Test immutability
    with pytest.raises(AttributeError):
        content.content = "# Changed"  # type: ignore


def test_read_markdown_with_dashes_in_content():
    """Test reading Markdown file with --- in content (not front matter)"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "test.md")
        # --- not at the start, so not front matter
        content = """# Hello

---

This is a separator.
"""
        kf.write_text(md_path, content)

        result = kf.read_markdown(md_path)

        assert result is not None
        assert result.metadata == {}
        assert result.content == content
