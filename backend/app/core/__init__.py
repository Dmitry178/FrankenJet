from app.config.env import settings
from app.core.cache_manager import CacheManager
from app.core.es_manager import ESManager
from app.core.http_manager import HTTPManager
from app.core.rmq_manager import RMQManager

# инициализация RabbitMQ-менеджера
rmq_manager = RMQManager(url=settings.RMQ_CONN)

# инициализация Cache-менеджера на основе Fastapi-cache2
cache_manager = CacheManager(url=settings.REDIS_URL, password=settings.REDIS_PASSWORD)

# инициализация ElasticSearch
es_manager = ESManager(url=settings.ELASTICSEARCH_URL)

# инициализация AIOHTTP менеджер сессий
http_manager = HTTPManager()
