from typing import Any, cast

from pydantic import BaseModel, Field

from kiarina.agi.tool_info import ToolName
from kiarina.i18n import Language, get_translator


class AdditionalFieldConfig(BaseModel):
    name: str
    """Field name"""

    type_hint: str
    """
    Field type hint

    e.g., "str", "int", "float", "bool", "list[str]", "dict[str, int]", etc.
    """

    description: str
    """Field description"""

    i18n_scope: str | None = None
    """I18n scope for description translation (empty = use description as-is)"""

    i18n_key: str | None = None
    """I18n key for description translation (empty = use description as-is)"""

    apply_to: list[ToolName] = Field(default_factory=list)
    """
    Tool names to apply this field to

    An empty list means the field should be applied to all tools.
    """

    @property
    def type(self) -> type[Any]:
        basic_types = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "dict": dict,
            "list": list,
            "tuple": tuple,
            "set": set,
        }

        if self.type_hint in basic_types:
            return basic_types[self.type_hint]

        try:
            return cast(
                type[Any], eval(self.type_hint, {"__builtins__": {}}, basic_types)
            )
        except Exception:
            return str

    def should_apply_to(self, tool_name: ToolName) -> bool:
        if not self.apply_to:
            return True

        return tool_name in self.apply_to

    def get_description(self, language: Language | None = None) -> str:
        if not self.i18n_scope or not self.i18n_key or not language:
            return self.description

        t = get_translator(language, self.i18n_scope)
        return t(self.i18n_key, default=self.description)
