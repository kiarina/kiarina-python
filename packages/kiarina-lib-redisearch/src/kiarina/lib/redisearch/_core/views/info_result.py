from pydantic import BaseModel, Field

from kiarina.lib.redisearch_schema import RedisearchSchema


class InfoResult(BaseModel):
    """Information returned by the Redis `FT.INFO` command."""

    index_name: str = Field(
        title="Index Name",
        description="Name of the index.",
    )
    num_docs: int = Field(
        title="Document Count",
        description="Number of documents in the index.",
    )
    num_terms: int = Field(
        title="Term Count",
        description="Number of terms in the index.",
    )
    num_records: int = Field(
        title="Record Count",
        description="Number of records in the index.",
    )
    index_schema: RedisearchSchema = Field(
        title="Index Schema",
        description="Schema reported by RediSearch.",
    )
