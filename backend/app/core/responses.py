from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool
    data: Any
    message: str


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel):
    success: bool
    data: Any
    message: str
    pagination: PaginationMeta


def success_response(data: Any = None, message: str = "OK") -> dict:
    """Return a standard success response dict."""
    return ApiResponse(success=True, data=data, message=message).model_dump()


def paginated_response(
    items: list,
    page: int,
    page_size: int,
    total: int,
    message: str = "OK",
) -> dict:
    """Return a paginated success response dict with pagination metadata."""
    return PaginatedResponse(
        success=True,
        data=items,
        message=message,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        ),
    ).model_dump()
