from fastapi import Depends
from typing import Annotated

from app.db.db_manager import DBManager
from app.db.init_db import async_session_maker


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

DDB = Annotated[DBManager, Depends(get_db)]
