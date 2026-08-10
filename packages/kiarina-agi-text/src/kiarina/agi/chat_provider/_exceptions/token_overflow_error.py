class TokenOverflowError(Exception):
    def __init__(self, token_count: int) -> None:
        self.token_count: int = token_count
        super().__init__(f"Token overflow error: {token_count} tokens")
