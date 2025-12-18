from copy import deepcopy
from typing import Any, TypeVar

from pydantic import BaseModel, create_model

from ...i18n._models.i18n import I18n

T = TypeVar("T", bound=BaseModel)


def create_pydantic_schema(
    pydantic_model: type[T],
    i18n_model: type[I18n],
) -> type[I18n]:
    """
    Create a Pydantic schema with field descriptions from I18n model.

    This function creates a new I18n subclass that:
    - Copies field structure from pydantic_model
    - Sets field descriptions from i18n_model's default values
    - Uses i18n_model's __doc__ as the schema's docstring
    - Inherits i18n_model's scope for translation

    Args:
        pydantic_model: Source Pydantic model to copy field structure from
        i18n_model: I18n model containing default descriptions and scope

    Returns:
        New I18n subclass with combined structure and descriptions

    Example:
        ```python
        from pydantic import BaseModel
        from kiarina.i18n import I18n, create_pydantic_schema

        class HogeI18n(I18n, scope="hoge"):
            \"\"\"Hoge tool\"\"\"
            name: str = "Your Name"
            age: str = "Your Age"

        class ArgsSchema(BaseModel):
            name: str
            age: int

        # Create schema with descriptions from I18n
        Schema = create_pydantic_schema(ArgsSchema, HogeI18n)

        # Schema now has:
        # - __doc__ = "Hoge tool"
        # - name field with description "Your Name"
        # - age field with description "Your Age"
        # - _scope = "hoge"
        ```
    """
    # Create default instance of i18n_model to get default values
    i18n_instance = i18n_model.model_construct()

    # Build new fields with descriptions from i18n_model
    new_fields: dict[str, Any] = {}

    for field_name, field_info in pydantic_model.model_fields.items():
        # Get description from i18n_model if field exists
        description = None

        if hasattr(i18n_instance, field_name):
            description = getattr(i18n_instance, field_name)

        # Get annotation (type)
        annotation = field_info.annotation if field_info.annotation is not None else Any

        # Copy the original FieldInfo and update description
        new_field_info = deepcopy(field_info)

        if description is not None:
            new_field_info.description = description

        new_fields[field_name] = (annotation, new_field_info)

    # Get __doc__ from i18n_model
    doc = i18n_model.__doc__ or pydantic_model.__doc__ or ""

    # Create new model class inheriting from I18n
    # Use i18n_model's scope
    schema_class = create_model(
        pydantic_model.__name__,
        __config__=pydantic_model.model_config,
        __doc__=doc,
        __base__=(I18n,),
        __module__=pydantic_model.__module__,
        **new_fields,
    )

    # Set scope from i18n_model
    schema_class._scope = i18n_model._scope

    return schema_class
