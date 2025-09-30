from fastapi import Depends
from typing import Annotated

from app.core import rmq_manager, RMQManager


async def get_rmq() -> RMQManager:
    """
    Dependency для FastAPI, возвращающий синглтон RMQManager
    """

    return rmq_manager

DRmq = Annotated[RMQManager, Depends(get_rmq)]
