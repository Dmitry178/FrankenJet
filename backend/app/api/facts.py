from fastapi import APIRouter, Depends, Body, Path

from app.core.logs import logger
from app.dependencies.auth import get_auth_editor_id, get_auth_admin_id
from app.dependencies.db import DDB
from app.exceptions.api import record_was_not_found_404
from app.exceptions.base import BaseCustomException
from app.schemas.api import SuccessResponse
from app.services.facts import FactsServices
from app.types import status_ok

facts_router = APIRouter(prefix="/facts", tags=["Facts"])


# TODO: сделать вывод фактов (GET) с пагинацией и фильтром

@facts_router.post("", summary="Добавление факта", dependencies=[Depends(get_auth_editor_id)])
async def add_fact(
        db: DDB,
        fact: str = Body(..., embed=True, max_length=256, description="Факт об авиации")
):
    """
    Добавление факта об авиации
    """

    try:
        data = await FactsServices(db).add_fact(fact)
        return {**status_ok, "data": data}

    except BaseCustomException as ex:
        logger.error(ex)
        return ex.json_response


@facts_router.put(
    "/{fact_id}",
    summary="Изменение факта",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_fact(
        db: DDB,
        fact_id: int = Path(...),
        fact: str = Body(..., embed=True, max_length=256, description="Факт об авиации")
):
    """
    Редактирование факта об авиации (put)
    """

    try:
        result = await FactsServices(db).edit_fact(fact_id, fact)
        return {**status_ok, "data": result} if result else record_was_not_found_404

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@facts_router.delete(
    "/{fact_id}",
    summary="Удаление факта",
    dependencies=[Depends(get_auth_admin_id)],
)
async def delete_fact(
        db: DDB,
        fact_id: int = Path(...)
):
    """
    Удаление факта об авиации
    """

    try:
        row_count = await FactsServices(db).delete_fact(fact_id)
        return SuccessResponse(data={"rows": row_count})

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
