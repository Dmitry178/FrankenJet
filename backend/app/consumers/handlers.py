import json

from app.config.app import RMQ_BACKEND_QUEUE
from app.core import rmq_manager


@rmq_manager.subscriber(RMQ_BACKEND_QUEUE)
async def handle_backend_response(message: str):
    data = json.loads(message)
    print("Получено сообщение от бота:", data)
