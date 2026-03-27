from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.session import async_engine

router = APIRouter(tags=["Health"])


@router.get("/healthz")
async def healthz() -> dict:
    return {
        "success": True,
        "data": {"status": "ok"},
        "message": "Application is running",
    }


@router.get("/readyz", status_code=status.HTTP_200_OK)
async def readyz() -> JSONResponse:
    try:
        async with async_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "data": {"status": "not_ready"},
                "message": "Database connection failed",
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": {"status": "ready"},
            "message": "Application and database are ready",
        },
    )
