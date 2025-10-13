from fastapi import APIRouter, Query

from app.core.logs import logger
from app.dependencies.db import DDB
from app.dependencies.es import DES
from app.schemas.search import SSearch
from app.services.search import SearchService
from app.types import status_error, status_ok

search_router = APIRouter(prefix="/search", tags=["Search"])


@search_router.post("", summary="Поиск")
async def search(
        db: DDB,
        es: DES,
        data: SSearch,
):
    """
    Поиск по всем сущностям
    """

    if not data.query:
        return {**status_error, "detail": "Пустой запрос"}

    try:
        result = await SearchService(db, es).search(data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error
