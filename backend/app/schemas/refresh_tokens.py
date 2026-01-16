from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SRefreshTokens(BaseModel):
    """
    Схема refresh-токенов (jti)
    """

    id: int
    user_id: UUID
    jti: UUID
    issued_at: datetime
    expired_at: datetime
    user_agent: str | None = Field(None, max_length=256)
