from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    # Название приложения
    APP_NAME: str = "Vectorizer"

    # Модель
    MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    FASTEMBED_CACHE_DIR: str | None = None

    # Параметры gRPC сервера
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50051

    # Максимальная длина текста
    MAX_TEXT_LENGTH: int = 2048


app_settings = Settings()
