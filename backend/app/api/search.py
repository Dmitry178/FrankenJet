from fastapi import APIRouter

from app.core.logs import logger
from app.dependencies.db import DDB
from app.dependencies.es import DES
from app.exceptions.base import BaseCustomException
from app.schemas.api import ApiResponse
from app.schemas.search import SSearch
from app.services.search import SearchService
from app.types import status_ok

search_router = APIRouter(prefix="/search", tags=["Pages"])


@search_router.post("", summary="Поиск")
async def search(db: DDB, es: DES, data: SSearch):
    """
    Поиск по всем сущностям
    """

    if not data.query:
        return ApiResponse.error("Пустой запрос")

    try:
        result = await SearchService(db, es).search(data)
        return {**status_ok, "data": result}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
