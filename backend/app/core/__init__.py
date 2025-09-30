from app.config.env import settings
from app.core.rmq_manager import RMQManager

# инициализация RabbitMQ-менеджера
rmq_manager = RMQManager(url=settings.RMQ_CONN, max_retries=3)
