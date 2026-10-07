DISABLED_FEATURES = (
    "apps",
    "browser_use",
    "browser_use_external",
    "code_mode_host",
    "computer_use",
    "goals",
    "hooks",
    "image_generation",
    "in_app_browser",
    "memories",
    "multi_agent",
    "plugins",
    "shell_tool",
    "skill_search",
    "sleep_tool",
    "tool_suggest",
    "unified_exec",
    "view_image",
    "workspace_dependencies",
)
"""Codex's own tools and agent features, turned off so only the caller's tools remain."""

DISABLED_INSTRUCTIONS = (
    "include_apps_instructions",
    "include_collaboration_mode_instructions",
    "include_environment_context",
    "include_permissions_instructions",
    "skills.include_instructions",
)
"""Instructions Codex adds about its environment and features."""
