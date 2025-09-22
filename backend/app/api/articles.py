from fastapi import APIRouter, Path, Query, Depends
from uuid import UUID

from app.core.logs import logger
from app.dependencies.auth import get_auth_editor_id
from app.dependencies.db import DDB
from app.schemas.articles import SArticles
from app.services.articles import ArticlesServices
from app.types import status_ok, status_error

articles_router = APIRouter(prefix="/articles", tags=["Articles"])


@articles_router.get("/{slug}", summary="Статья")
async def get_article(
        db: DDB,
        slug: str = Path(..., description=""),
):
    """
    Получение статьи
    """

    try:
        data = await ArticlesServices(db).get_article(slug)
        return {**status_ok, "data": data}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@articles_router.get("/list", summary="Статьи")
async def get_article_list(
        db: DDB,
        filters: str | None = Query(None, description="Фильтр"),
        page: int = Query(1, ge=1, description="Номер страницы"),
        page_size: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
):
    """
    Получение списка статей с фильтром
    """

    try:
        data = await ArticlesServices(db).get_articles_list(page, page_size, filters)
        return {**status_ok, "data": data}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@articles_router.post(
    "",
    summary="Добавление статьи",
    dependencies=[Depends(get_auth_editor_id)],
)
async def add_article(data: SArticles, db: DDB):
    """
    Добавление статьи
    """

    try:
        result = ArticlesServices(db).add_article(data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@articles_router.put(
    "/{article_id}",
    summary="Изменение статьи",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_article_put(article_id: UUID, data: SArticles, db: DDB):
    """
    Редактирование статьи (put)
    """

    try:
        result = ArticlesServices(db).edit_article(article_id, data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@articles_router.patch(
    "/{article_id}",
    summary="Изменение статьи",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_article_post(article_id: UUID, data: SArticles, db: DDB):
    """
    Редактирование статьи (patch)
    """

    try:
        result = ArticlesServices(db).edit_article(article_id, data, exclude_unset=True)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@articles_router.delete(
    "/{article_id}",
    summary="Удаление статьи",
    dependencies=[Depends(get_auth_editor_id)],
)
async def delete_article(article_id: UUID, db: DDB):
    """
    Удаление статьи
    """

    try:
        result = ArticlesServices(db).delete_article(article_id)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error
