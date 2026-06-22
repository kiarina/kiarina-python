from pydantic import BaseModel

from kiarina.i18n import I18n
from kiarina.i18n._helpers.resolve_i18n_scope import resolve_i18n_scope


def test_resolve_i18n_scope_uses_i18n_class_scope() -> None:
    class MyI18n(I18n, scope="custom.scope"):
        title: str = "Title"

    assert resolve_i18n_scope(MyI18n) == "custom.scope"


def test_resolve_i18n_scope_uses_auto_i18n_scope() -> None:
    class MyI18n(I18n):
        title: str = "Title"

    assert (
        resolve_i18n_scope(MyI18n)
        == "tests.i18n._helpers.test_resolve_i18n_scope.MyI18n"
    )


def test_resolve_i18n_scope_uses_base_model_module() -> None:
    class MyModel(BaseModel):
        title: str = "Title"

    MyModel.__module__ = "my_app.profile.text"

    assert resolve_i18n_scope(MyModel) == "my_app.profile.text"


def test_resolve_i18n_scope_uses_public_module_before_private_word() -> None:
    class MyModel(BaseModel):
        title: str = "Title"

    MyModel.__module__ = "my_app.profile._schemas.user"

    assert resolve_i18n_scope(MyModel) == "my_app.profile"
