class SafetyError(Exception):
    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "A safety error has occurred."

        super().__init__(message)
