from enum import Enum

from pydantic import AnyUrl, BeforeValidator, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Annotated

from typing_extensions import Self


class AppMode(str, Enum):
    """
    Режимы работы приложения
    """

    local = "local"
    test = "test"
    production = "production"


def parse_cors(v: Any) -> list[str] | str:
    """
    Парсинг CORS
    """

    if not v:
        return []

    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]

    elif isinstance(v, list | str):
        return v

    raise ValueError(v)


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    APP_NAME: str = "Franken Jet"  # название приложения
    APP_MODE: AppMode = AppMode.local  # режим работы приложения

    VERSION: str = "0"  # версия приложения  # TODO: добавить получение версии из файла в режиме local

    JWT_ALGORITHM: str = "HS256"  # TODO: переделать на RS256
    JWT_SECRET_KEY: str = "secret key"  # TODO: добавить возможность использования сертификатов
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 30  # время жизни jwt-токена (в минутах)

    DB_CONN: str  # строка соединения с базой

    # OAUTH2 аутентификация
    OAUTH2_GOOGLE_CLIENT_ID: str | None = None
    OAUTH2_GOOGLE_CLIENT_SECRET: str | None = None
    OAUTH2_VK_CLIENT_ID: str | None = None
    OAUTH2_VK_CLIENT_SECRET: str | None = None

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.DB_CONN}"

    CORS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []  # список CORS

    @computed_field
    @property
    def get_cors(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.CORS]

    @model_validator(mode="after")
    def _check_app_mode(self) -> Self:
        if self.APP_MODE not in AppMode.__members__:
            raise ValueError("Invalid application mode")
        return self

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
