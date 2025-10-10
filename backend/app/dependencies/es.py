from fastapi import Depends
from typing import Annotated

from app.core import ESManager, es_manager


async def get_es():
    """
    Dependency для FastAPI, предоставляющий ESManager
    """

    return es_manager


DES = Annotated[ESManager, Depends(get_es)]
