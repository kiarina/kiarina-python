import os
import tempfile

import pytest

import kiarina.utils.file.asyncio as kfa


@pytest.mark.asyncio
async def test_read_markdown_with_front_matter():
    """Test reading Markdown file with YAML front matter asynchronously"""
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
        await kfa.write_text(md_path, content)

        # Read the Markdown file
        result = await kfa.read_markdown(md_path)

        assert result is not None
        assert result.metadata["title"] == "Test Document"
        assert result.metadata["author"] == "John Doe"
        # YAML parses dates as datetime.date objects
        assert str(result.metadata["date"]) == "2025-01-01"
        assert result.metadata["tags"] == ["test", "markdown"]
        assert result.content == "# Hello World\n\nThis is a test document.\n"


@pytest.mark.asyncio
async def test_read_markdown_without_front_matter():
    """Test reading Markdown file without front matter asynchronously"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "test.md")
        content = "# Hello World\n\nThis is a test document.\n"
        await kfa.write_text(md_path, content)

        result = await kfa.read_markdown(md_path)

        assert result is not None
        assert result.metadata == {}
        assert result.content == content


@pytest.mark.asyncio
async def test_read_markdown_with_invalid_front_matter():
    """Test reading Markdown file with invalid YAML front matter asynchronously"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "test.md")
        # Invalid YAML (missing colon)
        content = """---
title Test Document
author: John Doe
---

# Hello World
"""
        await kfa.write_text(md_path, content)

        result = await kfa.read_markdown(md_path)

        assert result is not None
        # Invalid YAML should be treated as regular content
        assert result.metadata == {}
        assert result.content == content


@pytest.mark.asyncio
async def test_read_markdown_non_existent_file():
    """Test reading non-existent Markdown file asynchronously"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "non_existent.md")

        result = await kfa.read_markdown(md_path)
        assert result is None


@pytest.mark.asyncio
async def test_read_markdown_with_default():
    """Test reading non-existent Markdown file with default value asynchronously"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "non_existent.md")

        default = kfa.MarkdownContent(content="Default content", metadata={})
        result = await kfa.read_markdown(md_path, default=default)

        assert result is not None
        assert result.content == "Default content"
        assert result.metadata == {}


@pytest.mark.asyncio
async def test_read_markdown_empty_file():
    """Test reading empty Markdown file asynchronously"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = os.path.join(tmp_dir, "empty.md")
        await kfa.write_text(md_path, "")

        result = await kfa.read_markdown(md_path)

        assert result is not None
        assert result.content == ""
        assert result.metadata == {}


@pytest.mark.asyncio
async def test_read_markdown_with_complex_metadata():
    """Test reading Markdown file with complex nested metadata asynchronously"""
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
        await kfa.write_text(md_path, content)

        result = await kfa.read_markdown(md_path)

        assert result is not None
        assert result.metadata["title"] == "Complex Document"
        assert result.metadata["author"]["name"] == "John Doe"
        assert result.metadata["author"]["email"] == "john@example.com"
        assert result.metadata["tags"] == ["python", "markdown"]
        assert result.metadata["settings"]["draft"] is False
        assert result.metadata["settings"]["published"] is True
        assert result.content == "# Content\n"


def test_markdown_content_from_text_with_front_matter():
    """Test MarkdownContent.from_text() with YAML front matter"""
    text = """---
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
    result = kfa.MarkdownContent.from_text(text)

    assert result.metadata["title"] == "Test Document"
    assert result.metadata["author"] == "John Doe"
    assert str(result.metadata["date"]) == "2025-01-01"
    assert result.metadata["tags"] == ["test", "markdown"]
    assert result.content == "# Hello World\n\nThis is a test document.\n"


def test_markdown_content_from_text_without_front_matter():
    """Test MarkdownContent.from_text() without front matter"""
    text = "# Hello World\n\nThis is a test document.\n"
    result = kfa.MarkdownContent.from_text(text)

    assert result.metadata == {}
    assert result.content == text


def test_markdown_content_from_text_with_invalid_front_matter():
    """Test MarkdownContent.from_text() with invalid YAML front matter"""
    # Invalid YAML (missing colon)
    text = """---
title Test Document
author: John Doe
---

# Hello World
"""
    result = kfa.MarkdownContent.from_text(text)

    # Invalid YAML should be treated as regular content
    assert result.metadata == {}
    assert result.content == text
