from pydantic import BaseModel, Field


class URIPolicy(BaseModel):
    """URI access rules and directory templates for an asset repository."""

    allowed_uri_patterns: list[str] = Field(
        default_factory=list,
        title="Allowed URI Patterns",
        description="Regular expressions for URIs that the repository may access.",
    )
    data_dir_uri_template: str = Field(
        default="{invalid}",
        title="Data Directory URI Template",
        description="URI template for persistent asset data.",
    )
    cache_dir_uri_template: str = Field(
        default="{invalid}",
        title="Cache Directory URI Template",
        description="URI template for cached asset data.",
    )
