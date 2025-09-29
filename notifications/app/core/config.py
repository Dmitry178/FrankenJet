from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

# очереди RabbitMQ
RMQ_NOTIFICATIONS_QUEUE: str = "notification"  # уведомления бота
RMQ_ADMIN_AUTH_QUEUE: str = "admin_auth"  # уведомление об аутентификации админа
RMQ_MODERATION_QUEUE: str = "moderation"  # комментарии на модерацию
RMQ_BACKEND_QUEUE: str = "backend_bot"  # очередь отправки сообщения в бэкенд


class BotAppMode(str, Enum):
    """
    Режимы работы приложения
    """

    local = "local"
    test = "test"
    production = "production"


class BotSettings(BaseSettings):
    """
    Настройки приложения
    """

    APP_NAME: str = "Franken Jet Notification Bot"  # название приложения
    APP_MODE: BotAppMode = BotAppMode.local  # режим работы приложения
    BUILD: str = "0"  # билд приложения

    RMQ_CONN: str | None = None  # строка подключения к RabbitMQ

    # telegram id учётной записи админа (на данном этапе - единичная запись)
    TELEGRAM_ADMIN_ID: str | None = None
    TELEGRAM_API_TOKEN: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


bot_settings = BotSettings()
