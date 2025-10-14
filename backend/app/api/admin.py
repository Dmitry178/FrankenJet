from fastapi import APIRouter, UploadFile, File
from starlette import status
from starlette.responses import JSONResponse

from app.core.logs import logger
from app.dependencies.db import DDB
from app.exceptions.base import BaseCustomException
from app.schemas.api import ApiResponse, ErrorResponse
from app.services.admin import AdminServices

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.post("/uploads", summary="Загрузка файлов")
async def uploads(db: DDB, file: UploadFile = File(...)):
    """
    Загрузка zip-файла и обработка данных
    """

    try:
        if file.content_type != "application/zip":
            raise ValueError("Файл должен быть в формате ZIP")

        await AdminServices(db).upload_file(file)
        return ApiResponse.success()

    except ValueError as ex:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(detail=ex.args[0] if ex.args else None).model_dump()
        )

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
