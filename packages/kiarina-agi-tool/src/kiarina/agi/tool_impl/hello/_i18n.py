from kiarina.i18n import I18n


class HelloToolI18n(I18n, scope="kiarina.agi.tool_impl.hello"):
    hello_completed: str = "Hello"
