class SafetyError(Exception):
    def __init__(
        self,
        message: str | None = None,
        *,
        category: str | None = None,
        request_id: str | None = None,
    ) -> None:
        if message is None:
            message = "A safety error has occurred."

        self.category: str | None = category
        self.request_id: str | None = request_id
        super().__init__(message)
