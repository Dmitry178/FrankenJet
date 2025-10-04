from fastapi import Depends
from typing import Annotated

from app.core.db_manager import DBManager
from app.db import async_session_maker


async def get_db():
    """
    Dependency для FastAPI, предоставляющий DBManager
    """

    async with DBManager(session_factory=async_session_maker) as db:
        yield db

DDB = Annotated[DBManager, Depends(get_db)]
