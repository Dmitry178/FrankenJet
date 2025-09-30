from app.core import rmq_manager
from . import handlers  # noqa: F401


async def run_consumers():
    """
    Запуск консьюмеров (для режима локальной разработки)
    """

    await rmq_manager.run_consumers()
