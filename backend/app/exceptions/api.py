""" Общие исключения для API """

from fastapi import HTTPException
from starlette import status
from starlette.responses import JSONResponse

from app.types import status_error

forbidden_403 = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

http_error_500 = JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={**status_error, "detail": "Ошибка сервиса"}
)

rabbitmq_not_available = JSONResponse(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    content={**status_error, "detail": "Брокер сообщений не установлен"}
)

settings_error = JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={**status_error, "detail": "Ошибка получения настроек приложения"}
)
