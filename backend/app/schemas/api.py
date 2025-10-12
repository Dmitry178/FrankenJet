from pydantic import BaseModel


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
