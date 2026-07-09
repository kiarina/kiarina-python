from kiarina.i18n import I18n


class WaitToolI18n(I18n, scope="kiarina.agi.tool_impl.wait"):
    wait_completed: str = "Waited for {wait_time} seconds."
