from fastapi import HTTPException
from starlette import status
from starlette.responses import JSONResponse

from app.schemas.api import ErrorResponse


class BaseCustomException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad Request"

    def __init__(self, *args, **kwargs):  # noqa
        super().__init__(self.detail, *args)

    @property
    def json_response(self):
        return JSONResponse(
            status_code=self.status_code,
            content=ErrorResponse(detail=self.detail).model_dump()
        )

    @property
    def http_exception(self):
        raise HTTPException(status_code=self.status_code, detail=self.detail)


class DatabaseNoResultError(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Объект не найден"


class DatabaseMultipleResultsError(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Множественные объекты"


class DatabaseUniqueFieldError(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Объект уже существует"


class DatabaseServiceError(BaseCustomException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Ошибка базы данных"


class DatabaseUpdateError(BaseCustomException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Ошибка обновления данных"


class ServiceError(BaseCustomException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка сервиса"
