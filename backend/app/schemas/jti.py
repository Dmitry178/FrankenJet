from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SRefreshTokens(BaseModel):
    """
    Схема refresh-токенов (jti)
    """

    id: int
    user_id: int
    jti: UUID
    issued_at: datetime
    revoked: bool
    user_agent: str | None = Field(None, max_length=256)
