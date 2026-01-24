from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

# очереди RabbitMQ
RMQ_FJ_OUTPUT_QUEUE = "fj_output"  # очередь для приёма сообщений ботом от бэкенда FrankenJet
RMQ_FJ_INPUT_QUEUE = "fj_input"  # очередь для приёма сообщения бэкендом FrankenJet от бота
RMQ_VECTORIZER_QUEUE = "vectorizer"  # очередь для приёма сообщений ботом от проекта Vectorizer


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

    APP_NAME: str = "FJ Notification Bot"  # название приложения
    APP_MODE: BotAppMode = BotAppMode.local  # режим работы приложения
    BUILD: str = "0"  # билд приложения

    RMQ_CONN: str | None = None  # строка подключения к RabbitMQ

    # telegram id учётной записи админа (на данном этапе - единичная запись)
    TELEGRAM_ADMIN_ID: int | str
    TELEGRAM_API_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


bot_settings = BotSettings()
