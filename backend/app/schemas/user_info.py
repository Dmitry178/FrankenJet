from pydantic import BaseModel


class SUserAgentInfo(BaseModel):
    """
    Схема подробной информации о user-agent
    """

    is_ru: bool  # есть ли "ru" в accept language
    is_bot: bool  # является ли пользователь ботом
    is_tablet: bool
    is_mobile: bool
    is_touch_capable: bool
    is_pc: bool
    os_family: str | None = None
    os_version: str | None = None
    device_family: str | None = None
    device_brand: str | None = None
    device_model: str | None = None
    browser_family: str | None = None
    browser_version: str | None = None


class SClientInfo(BaseModel):
    """
    Схема информации о клиенте
    """

    ip: str | None = None
    xff: str | None = None
    user_agent: str | None = None
    user_agent_parce: str | None = None
    real_ip: str | None = None
    referer: str | None = None
    accept_language: str | None = None
    user_agent_info: SUserAgentInfo | None = None
