from pydantic import BaseModel, Field


class FilePathPolicy(BaseModel):
    """Local file access rules and directory templates."""

    allowed_file_path_patterns: list[str] = Field(
        default_factory=lambda: [".*"],
        title="Allowed File Path Patterns",
        description="Regular expressions for file paths that the repository may access.",
    )
    data_dir_path_template: str = Field(
        default="{user_data_dir}/agents/{agent_id}",
        title="Data Directory Path Template",
        description="Path template for persistent data.",
    )
    cache_dir_path_template: str = Field(
        default="{user_cache_dir}/agents/{agent_id}",
        title="Cache Directory Path Template",
        description="Path template for cached data.",
    )
