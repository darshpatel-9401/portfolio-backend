class ApiError(Exception):
    """Raise this anywhere to send a JSON error like {"detail": "..."} to the client."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
