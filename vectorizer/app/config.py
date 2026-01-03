from pydantic_settings import BaseSettings

'''
Примеры моделей для FastEmbed:
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (384)

Примеры моделей для Sentence Transformers:
all-MiniLM-L6-v2 (384)
paraphrase-multilingual-MiniLM-L12-v2 (384)
intfloat/multilingual-e5-large (1024)
cointegrated/rubert-base-cased-nli-mean-tokens (768)
sberbank-ai/sbert_large_nlu_ru (1024)
'''

RMQ_QUEUE = "vectorizer"  # очередь для отправки сообщений в бот


class ModelLib:
    """
    Библиотеки эмбедингов
    """

    class FastEmbed:
        name = "fastembed"
        paraphrase_multilingual_MiniLM_L12_v2 = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # 384

    class SentenceTransformers:
        name = "sentence_transformers"
        all_MiniLM_L6_v2 = "all-MiniLM-L6-v2"  # 384
        paraphrase_multilingual_MiniLM_L12_v2 = "paraphrase-multilingual-MiniLM-L12-v2"  # 384
        multilingual_e5_large = "intfloat/multilingual-e5-large"  # 1024
        rubert_base_cased_nli_mean_tokens = "cointegrated/rubert-base-cased-nli-mean-tokens"  # 768
        sbert_large_nlu_ru = "sberbank-ai/sbert_large_nlu_ru"  # 1024

    fastembed = FastEmbed
    sentence_transformers = SentenceTransformers


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Название приложения
    APP_NAME: str = "Vectorizer"

    # Параметры модели
    MODEL_LIB: str = ModelLib.fastembed.name
    # MODEL_LIB: str = ModelLib.sentence_transformers.name
    MODEL_NAME: str = ModelLib.fastembed.paraphrase_multilingual_MiniLM_L12_v2
    # MODEL_NAME: str = ModelLib.sentence_transformers.all_MiniLM_L6_v2
    MODEL_CACHE_DIR: str | None = "./models/cache"

    # Параметры gRPC сервера
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50051

    # Параметры RabbitMQ
    RMQ_CONN: str | None = None


app_settings = Settings()
