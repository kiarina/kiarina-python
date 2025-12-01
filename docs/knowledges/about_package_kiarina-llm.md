---
title: About kiarina-llm package
description: >-
  kiarina-llm is a library for LLM utilities and context management
  with type safety and configuration management.
---

kiarina-llm provides utilities for LLM (Large Language Model) integration and pipeline processing.
Currently, it focuses on RunContext management for structured context information in LLM pipelines.

Key features include:
- RunContext management for LLM pipeline processing
- Type-safe context information with Pydantic validation
- Configuration management using pydantic-settings-manager
- Filesystem safe names for cross-platform compatibility
- ID validation with pattern checking
- Environment variable configuration

Future roadmap includes:
- Chat model management with unified interface for different LLM providers
- Agent framework for building LLM agents
- Pipeline management for LLM processing workflows
- Memory management for context and conversation handling
- Tool integration framework for LLM tool calling
