from app.config.chatbot import ChatBotSettingsManager
from app.config.env import settings
from app.core.cache_manager import CacheManager
from app.core.es_manager import ESManager
from app.core.http_manager import HTTPManager
from app.core.rmq_manager import RMQManager
from app.core.vectorizer import VectorizerManager
from app.core.ws_manager import WSManager

# инициализация RabbitMQ-менеджера
rmq_manager = RMQManager(url=settings.RMQ_CONN)

# инициализация Cache-менеджера на основе FastAPI-Cache2
cache_manager = CacheManager(url=settings.REDIS_URL)

# инициализация Elasticsearch-менеджера
es_manager = ESManager(
    url=settings.ELASTIC_URL,
    password=settings.ELASTIC_PASSWORD,
    use_ssl=settings.ELASTIC_USE_SSL
)

# инициализация AIOHTTP-менеджера сессий
http_manager = HTTPManager()

# инициализация Websocket-менеджера
ws_manager = WSManager()

# инициализация менеджера настроек чат-бота
chatbot_settings = ChatBotSettingsManager()

# инициализация менеджера векторизатора текста
vectorizer_manager = VectorizerManager(server_address=settings.VECTORIZER_GRPC_ADDRESS)
