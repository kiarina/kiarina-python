from kiarina.i18n import I18n


class ExitToolI18n(I18n, scope="kiarina.agi.tool_impl.exit"):
    exit_completed: str = "Exiting with code {code}: {message}"
