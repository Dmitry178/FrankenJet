from fastapi import APIRouter, Query

from app.core.logs import logger
from app.dependencies.db import DDB
from app.dependencies.es import DES
from app.services.search import SearchService
from app.types import status_error, status_ok

search_router = APIRouter(prefix="/search", tags=["Search"])


@search_router.get("", summary="Поиск")
async def search(
        db: DDB,
        es: DES,
        q: str | None = Query(None, max_length=256, description="Поисковый запрос"),
        categories: str | None = Query(None, max_length=128, description="Категории через запятую без пробела"),
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
):
    """
    Поиск по всем сущностям
    """

    if not q:
        return {**status_error, "detail": "empty_query", "message": "Пустой запрос"}

    try:
        data = await SearchService(db, es).search(q, categories, page, per_page)
        return {**status_ok, "data": data}

    except Exception as ex:
        logger.exception(ex)
        return status_error
