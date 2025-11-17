from fastapi import APIRouter, UploadFile, File, Depends
from starlette import status
from starlette.responses import JSONResponse, Response

from app.core.logs import logger
from app.dependencies.auth import get_auth_admin_id
from app.dependencies.db import DDB
from app.exceptions.base import BaseCustomException
from app.schemas.api import ErrorResponse
from app.services.admin import AdminServices
from app.types import status_ok

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.post("/uploads", summary="Загрузка статей (zip)", dependencies=[Depends(get_auth_admin_id)])
async def uploads(db: DDB, file: UploadFile = File(...)):
    """
    Загрузка статей и прочих данных энциклопедии в виде zip-файла
    """

    try:
        if file.content_type != "application/zip":
            raise ValueError("Файл должен быть в формате ZIP")

        await AdminServices(db).upload_file(file)
        return status_ok

    except ValueError as ex:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(detail=ex.args[0] if ex.args else None).model_dump()
        )

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@admin_router.get("/sitemap", summary="Генерация sitemap.xml", dependencies=[Depends(get_auth_admin_id)])
async def sitemap(db: DDB):
    """
    Генерация sitemap.xml
    """

    try:
        sitemap_xml = await AdminServices(db).sitemap()
        return Response(
            content=sitemap_xml,
            media_type="application/xml",
            headers={
                "Content-Disposition": 'attachment; filename="sitemap.xml"'
            }
        )

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
