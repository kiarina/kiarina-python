class TokenOverflowError(Exception):
    def __init__(self, token_count: int, *, limit: int | None = None) -> None:
        self.token_count: int = token_count
        # The maximum the vendor named with the overflow, when it did.
        self.limit: int | None = limit

        message = f"Token overflow error: {token_count} tokens"

        if limit is not None:
            message += f" > {limit} maximum"

        super().__init__(message)
