from app.schemas.api import ApiResponse
from app.types import StatusEnum


def test_schema_response_success():
    # тестируем .success() без данных
    response = ApiResponse.success()
    assert response.status == StatusEnum.ok
    assert response.data is None
    assert response.detail is None

    # тестируем .success() с данными
    test_data = {"key": "value"}
    response_with_data = ApiResponse.success(data=test_data)
    assert response_with_data.status == StatusEnum.ok
    assert response_with_data.data == test_data
    assert response_with_data.detail is None


def test_schema_response_error():
    # тестируем .error() без деталей
    response = ApiResponse.error()
    assert response.status == StatusEnum.error
    assert response.data is None
    assert response.detail is None

    # тестируем .error() с деталями
    error_detail = "Something went wrong"
    response_with_detail = ApiResponse.error(detail=error_detail)
    assert response_with_detail.status == StatusEnum.error
    assert response_with_detail.data is None
    assert response_with_detail.detail == error_detail


def test_schema_response_default():
    response = ApiResponse(status=StatusEnum.ok, data="test_data", detail="test_detail")
    assert response.status == StatusEnum.ok
    assert response.data == "test_data"
    assert response.detail == "test_detail"

    # проверка значений по умолчанию
    response_default = ApiResponse(status=StatusEnum.error)  # data и detail не передаем
    assert response_default.status == StatusEnum.error
    assert response_default.data is None  # проверяем, что data по умолчанию None
    assert response_default.detail is None  # проверяем, что detail по умолчанию None

