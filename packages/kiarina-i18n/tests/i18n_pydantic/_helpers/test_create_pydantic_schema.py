import pytest
from pydantic import BaseModel, Field

from kiarina.i18n import I18n, settings_manager
from kiarina.i18n_pydantic import create_pydantic_schema, translate_pydantic_model


def test_create_pydantic_schema_basic():
    """Test basic schema creation with I18n descriptions."""

    class HogeI18n(I18n, scope="hoge"):
        """Hoge tool"""

        name: str = "Your Name"
        age: str = "Your Age"

    class ArgsSchema(BaseModel):
        name: str
        age: int

    # Create schema
    Schema = create_pydantic_schema(ArgsSchema, HogeI18n)

    # Check model name is preserved
    assert Schema.__name__ == "ArgsSchema"

    # Check __doc__
    assert Schema.__doc__ == "Hoge tool"

    # Check scope
    assert Schema._scope == "hoge"

    # Check field descriptions
    assert Schema.model_fields["name"].description == "Your Name"
    assert Schema.model_fields["age"].description == "Your Age"

    # Check field types are preserved
    assert Schema.model_fields["name"].annotation is str
    assert Schema.model_fields["age"].annotation is int


def test_create_pydantic_schema_partial_fields():
    """Test schema creation when I18n has only some fields."""

    class HogeI18n(I18n, scope="hoge"):
        """Hoge tool"""

        name: str = "Your Name"
        # age is missing

    class ArgsSchema(BaseModel):
        name: str
        age: int

    # Create schema
    Schema = create_pydantic_schema(ArgsSchema, HogeI18n)

    # name should have description
    assert Schema.model_fields["name"].description == "Your Name"

    # age should have no description (None)
    assert Schema.model_fields["age"].description is None


def test_create_pydantic_schema_preserves_field_attributes():
    """Test that field attributes like default, min_length are preserved."""

    class HogeI18n(I18n, scope="hoge"):
        name: str = "Your Name"
        age: str = "Your Age"

    class ArgsSchema(BaseModel):
        name: str = Field(default="Anonymous", min_length=1)
        age: int = Field(default=0, ge=0)

    # Create schema
    Schema = create_pydantic_schema(ArgsSchema, HogeI18n)

    # Check defaults are preserved
    assert Schema.model_fields["name"].default == "Anonymous"
    assert Schema.model_fields["age"].default == 0

    # Check constraints are preserved
    name_field = Schema.model_fields["name"]
    age_field = Schema.model_fields["age"]

    # Pydantic v2 stores constraints in metadata
    assert name_field.metadata is not None
    assert age_field.metadata is not None

    # Create instance to verify validation works
    instance = Schema()
    assert instance.name == "Anonymous"  # type: ignore
    assert instance.age == 0  # type: ignore

    # Test validation
    with pytest.raises(Exception):  # ValidationError
        # Empty name (min_length=1)
        Schema(name="", age=0)  # type: ignore

    with pytest.raises(Exception):  # ValidationError
        # Negative age (ge=0)
        Schema(name="Alice", age=-1)  # type: ignore


def test_create_pydantic_schema_with_translate_pydantic_model():
    """Test that created schema can be translated with translate_pydantic_model."""

    class HogeI18n(I18n, scope="hoge"):
        """Hoge tool"""

        name: str = "Your Name"
        age: str = "Your Age"

    class ArgsSchema(BaseModel):
        name: str
        age: int

    # Configure catalog
    settings_manager.cli_args = {
        "catalog": {
            "ja": {
                "hoge": {
                    "__doc__": "Hogeツール",
                    "name": "あなたの名前",
                    "age": "あなたの年齢",
                }
            }
        }
    }

    # Create schema
    Schema = create_pydantic_schema(ArgsSchema, HogeI18n)

    # Translate schema (scope is auto-detected from Schema._scope)
    SchemaJa = translate_pydantic_model(Schema, "ja")

    # Check translated __doc__
    assert SchemaJa.__doc__ == "Hogeツール"

    # Check translated descriptions
    assert SchemaJa.model_fields["name"].description == "あなたの名前"
    assert SchemaJa.model_fields["age"].description == "あなたの年齢"


def test_create_pydantic_schema_without_docstring():
    """Test schema creation when I18n has no __doc__."""

    class HogeI18n(I18n, scope="hoge"):
        name: str = "Your Name"

    class ArgsSchema(BaseModel):
        name: str

    # Create schema
    Schema = create_pydantic_schema(ArgsSchema, HogeI18n)

    # __doc__ should be empty string (pydantic create_model sets it to "")
    # Note: In some cases it might be None, both are acceptable
    assert Schema.__doc__ in ("", None)


def test_create_pydantic_schema_inherits_i18n():
    """Test that created schema inherits from I18n."""

    class HogeI18n(I18n, scope="hoge"):
        name: str = "Your Name"

    class ArgsSchema(BaseModel):
        name: str

    # Create schema
    Schema = create_pydantic_schema(ArgsSchema, HogeI18n)

    # Should be subclass of I18n
    assert issubclass(Schema, I18n)

    # Should be frozen (I18n config)
    instance = Schema(name="Alice")
    with pytest.raises(Exception):  # ValidationError or AttributeError
        instance.name = "Bob"  # type: ignore


def test_create_pydantic_schema_multiple_schemas():
    """Test creating multiple schemas from different I18n models."""

    class HogeI18n(I18n, scope="hoge"):
        """Hoge tool"""

        name: str = "Your Name"

    class FugaI18n(I18n, scope="fuga"):
        """Fuga tool"""

        title: str = "Title"

    class HogeArgs(BaseModel):
        name: str

    class FugaArgs(BaseModel):
        title: str

    # Create schemas
    HogeSchema = create_pydantic_schema(HogeArgs, HogeI18n)
    FugaSchema = create_pydantic_schema(FugaArgs, FugaI18n)

    # Check they are independent
    assert HogeSchema.__doc__ == "Hoge tool"
    assert FugaSchema.__doc__ == "Fuga tool"
    assert HogeSchema._scope == "hoge"
    assert FugaSchema._scope == "fuga"
    assert HogeSchema.model_fields["name"].description == "Your Name"
    assert FugaSchema.model_fields["title"].description == "Title"


def test_create_pydantic_schema_with_extra_i18n_fields():
    """Test that extra fields in I18n (not in pydantic_model) are ignored."""

    class HogeI18n(I18n, scope="hoge"):
        """Hoge tool"""

        name: str = "Your Name"
        note: str = "This is a note"  # Extra field not in ArgsSchema
        error_message: str = "Error occurred"  # Extra field

    class ArgsSchema(BaseModel):
        name: str

    # Create schema
    Schema = create_pydantic_schema(ArgsSchema, HogeI18n)

    # Should only have 'name' field
    assert "name" in Schema.model_fields
    assert "note" not in Schema.model_fields
    assert "error_message" not in Schema.model_fields

    # name should have description
    assert Schema.model_fields["name"].description == "Your Name"


def test_create_pydantic_schema_json_schema():
    """Test that JSON schema includes descriptions."""

    class HogeI18n(I18n, scope="hoge"):
        """Hoge tool"""

        name: str = "Your Name"
        age: str = "Your Age"

    class ArgsSchema(BaseModel):
        name: str
        age: int

    # Create schema
    Schema = create_pydantic_schema(ArgsSchema, HogeI18n)

    # Get JSON schema
    json_schema = Schema.model_json_schema()

    # Check descriptions in schema
    assert json_schema["properties"]["name"]["description"] == "Your Name"
    assert json_schema["properties"]["age"]["description"] == "Your Age"
