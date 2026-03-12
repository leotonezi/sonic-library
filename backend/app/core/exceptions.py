class RateLimitExceeded(Exception):
    """Raised when a user exceeds the rate limit."""

    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Try again in {retry_after} seconds.")
