from fastapi import Depends
from typing import Annotated

from app.db import async_session_maker
from app.db.db_manager import DBManager


async def get_db():
    """
    Dependency для FastAPI, предоставляющий DBManager
    """

    async with DBManager(session_factory=async_session_maker) as db:
        yield db

DDB = Annotated[DBManager, Depends(get_db)]
