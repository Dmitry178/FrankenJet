from pydantic import BaseModel
from typing import Any

from app.types import StatusEnum


class SuccessResponse(BaseModel):
    status: str = StatusEnum.ok
    data: Any | None = None


class ErrorResponse(BaseModel):
    status: str = StatusEnum.error
    detail: str | None = None


class ApiResponse(BaseModel):
    status: StatusEnum
    data: Any | None = None
    detail: str | None = None

    @classmethod
    def success(cls, data: Any = None):
        return cls(status=StatusEnum.ok, data=data)

    @classmethod
    def error(cls, detail: str | None = None):
        return cls(status=StatusEnum.error, detail=detail)


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
