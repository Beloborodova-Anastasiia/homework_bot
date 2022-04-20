class HasNoTokens(Exception):
    """Exception if has no availability of environment variables."""

    pass


class APIError(Exception):
    """Error accessing the API service."""

    pass


class EmptyDict(Exception):
    """Error dyctionary is empty."""

    pass


class KeyNotExists(Exception):
    """Key not exists in the dictionary."""

    pass
