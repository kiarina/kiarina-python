from kiarina.i18n import I18n


class FileInfoSectionI18n(I18n, scope="kiarina.agi.section_impl.file_info"):
    human_text: str = "These are files that may be relevant to the current task."
    ai_text: str = "Understood."
