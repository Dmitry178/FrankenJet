import json

from app.config.app import RMQ_FJ_INPUT_QUEUE
from app.core import rmq_manager


@rmq_manager.subscriber(RMQ_FJ_INPUT_QUEUE)
async def handle_backend_response(message: str):
    try:
        data = json.loads(message)
        print("Получено сообщение от бота:", data)
    except json.JSONDecodeError:
        pass
