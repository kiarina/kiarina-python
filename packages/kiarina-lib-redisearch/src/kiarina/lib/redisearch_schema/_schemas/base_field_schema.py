from pydantic import BaseModel, Field, field_validator


class BaseFieldSchema(BaseModel):
    """Base schema for a RediSearch field."""

    name: str = Field(
        title="Field Name",
        description="Field name. 'payload' and 'distance' are reserved.",
    )

    @field_validator("name")
    @classmethod
    def forbid_reserved_names(cls, v: str) -> str:
        reserved = {"payload", "distance"}

        if v in reserved:
            raise ValueError(f'"{v}" is a reserved name and cannot be used.')

        return v
