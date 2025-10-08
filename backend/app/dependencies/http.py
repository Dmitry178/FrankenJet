# Dependency с безопасными запросами

from fastapi import Depends
from typing import AsyncGenerator, Annotated

from app.core import HTTPManager, http_manager


async def get_http_session() -> AsyncGenerator[HTTPManager, None]:
    yield http_manager

DHTTP = Annotated[HTTPManager, Depends(get_http_session)]
