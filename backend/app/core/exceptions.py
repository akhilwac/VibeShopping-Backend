from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception with an HTTP status code and message."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class NotFoundException(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(status_code=404, message=message)


class UnauthorizedException(AppException):
    """Raised when authentication fails or credentials are invalid."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(status_code=401, message=message)


class BadRequestException(AppException):
    """Raised when the request payload or parameters are invalid."""

    def __init__(self, message: str = "Bad request") -> None:
        super().__init__(status_code=400, message=message)


class ConflictException(AppException):
    """Raised when an operation conflicts with the current state (e.g. duplicate)."""

    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(status_code=409, message=message)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers that return the standard ApiResponse format."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "message": exc.message,
            },
        )

    @app.exception_handler(422)
    async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "data": None,
                "message": str(exc),
            },
        )

    @app.exception_handler(500)
    async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "message": "Internal server error",
            },
        )
