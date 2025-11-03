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

    def __str__(self) -> str:
        return self.value


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
    BUILD: str = "0"  # версия приложения  # TODO: добавить получение билда из файла в режиме local

    JWT_SECRET_KEY: str = "secret key"  # TODO: добавить возможность использования сертификатов

    DB_CONN: str  # строка соединения с базой
    RMQ_CONN: str | None = None  # строка подключения к RabbitMQ
    REDIS_URL: str | None = None  # строка подключения к Redis
    ELASTICSEARCH_URL: str | None = None  # строка подключения к ElasticSearch
    ELASTICSEARCH_PASSWORD: str | None = None  # пароль к ElasticSearch

    # подключение к S3
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_ENDPOINT_URL: str | None = None  # url для API
    S3_DIRECT_URL: str | None = ""  # url для доступа к данным в S3

    # учётная запись админа по умолчанию (создаётся при первом запуске)
    ADMIN_USER: str | None = None
    ADMIN_PASS: str | None = None

    # доступность встроенной аутентификации, регистрации и сброса пароля пользователя
    ALLOW_AUTHENTICATION: bool = False
    ALLOW_REGISTRATION: bool = False
    ALLOW_RESET_PASSWORD: bool = False
    ALLOW_OAUTH2_GOOGLE: bool = False
    ALLOW_OAUTH2_VK: bool = False

    # OAUTH2 аутентификация
    OAUTH2_GOOGLE_CLIENT_ID: str | None = None
    OAUTH2_GOOGLE_CLIENT_SECRET: str | None = None
    OAUTH2_VK_CLIENT_ID: str | None = None
    OAUTH2_VK_CLIENT_SECRET: str | None = None

    # эта настройка исключает проверку CSRF-токена для Swagger UI и ReDoc в production,
    # для локальной разработки всегда отключено, по умолчанию отключено
    SWAGGER_CSRF_EXCLUDE_IN_PROD: bool = False

    # доступен ли Swagger UI и ReDoc в production, по умолчанию отключено
    SWAGGER_AVAILABLE_IN_PROD: bool = False

    # префикс для Swagger UI, ReDoc и OpenAPI
    SWAGGER_URL_PREFIX: str = ""

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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
