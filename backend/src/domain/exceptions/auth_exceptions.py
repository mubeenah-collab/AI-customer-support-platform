class AuthException(Exception):
    """Base domain exception for authentication errors."""

    def __init__(self, message: str = "Authentication error"):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistsError(AuthException):
    """Raised when registering a user with an email that is already registered."""

    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists.")


class InvalidCredentialsError(AuthException):
    """Raised when authentication credentials (email/password) are invalid."""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)


class UnauthorizedError(AuthException):
    """Raised when a request lacks valid authentication credentials."""

    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message)


class ForbiddenError(AuthException):
    """Raised when an authenticated user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message)


class TokenExpiredError(AuthException):
    """Raised when a JWT token is expired."""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)
