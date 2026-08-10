from kiarina.i18n import I18n


class ConfirmHookI18n(I18n, scope="kiarina.agi.pre_hook_impl.confirm"):
    prompt_message: str = "Execute this tool? (yes/no) [yes]: "
    invalid_response: str = "Please enter yes/y or no/n."
    reason_prompt: str = "Reason for rejection (optional, press Enter to skip): "
    user_rejected: str = "User rejected tool execution"
    user_rejected_with_reason: str = "User rejected tool execution: {reason}"
