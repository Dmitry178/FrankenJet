from pydantic import BaseModel
from typing import Any

from app.types import status_ok, status_error


class SuccessResponse(BaseModel):
    status: str = status_ok.get("status")
    data: Any | None = None


class ErrorResponse(BaseModel):
    status: str = status_error.get("status")
    detail: str | None = None


ApiResponse = SuccessResponse | ErrorResponse  # стандартный ответ от API


class SClientInfo(BaseModel):
    """
    Схема информации о клиенте
    """

    ip: str | None = None
    xff: str | None = None
    user_agent: str | None = None
    real_ip: str | None = None
    referer: str | None = None
    accept_language: str | None = None
