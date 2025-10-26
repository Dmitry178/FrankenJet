from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from typing import Annotated

from app.config.app import JWT_TYPE_ACCESS
from app.core.logs import logger
from app.exceptions.auth import TokenTypeErrorEx, AuthRoleErrorEx, unauthorized_401, unauthorized_403
from app.schemas.auth import SAuthUserInfo
from app.services.security import SecurityService

security = HTTPBearer()

"""
В данном модуле намеренно нарушается принцип DRY (Don't Repeat Yourself) по следующим причинам.

1. Особенности реализации цепочки Depends() в FastAPI:  
  механизм Depends() предназначен для внедрения зависимостей, но не для передачи параметров (например, ролей)
  во время выполнения запроса.

2. Риски безопасности при параметризации get_auth_user_id():
  - технически возможно реализовать логику проверки ролей в функции get_auth_user_id()
    и передавать роли через параметры, однако, это сделает параметры ролей доступными непосредственно в API,
    сторонний пользователь сможет изменить эти параметры (например, подменить роль на "admin"),
    что приведет к несанкционированному повышению привилегий;
  - попытка передать роли через lambda-функции приводит к появлению параметров *args и **kwargs в сигнатуре эндпоинта,
    что так же позволяет стороннему пользователю подменять параметры (уже любые, не только роли), так же это
    потенциально может привести к нежелательному поведению, если эндпоинт начнёт принимать неверные аргументы.

3. Вывод:
   Наиболее безопасным и понятным решением является явное определение функций проверки ролей
   (get_auth_admin_id, get_auth_editor_id, get_auth_moderator_id) с дублированием логики проверки.
   Это позволяет избежать рисков, связанных с динамической передачей ролей через параметры эндпоинта или lambda-функции,
   даже ценой нарушения принципа DRY. Явное определение зависимостей для каждой роли делает код более предсказуемым
   и упрощает его аудит с точки зрения безопасности.
"""


async def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Получение токена из заголовков
    """

    return credentials.credentials


async def get_auth_token_payload(token: str = Depends(get_auth_token)) -> dict:
    """
    Получение значения токена из заголовков
    """

    try:
        token_payload = SecurityService.decode_token(token)
        if not token_payload:
            raise InvalidTokenError

        return token_payload

    except (ExpiredSignatureError, InvalidTokenError):
        raise unauthorized_401

    except Exception as ex:
        logger.exception(ex)
        raise Exception from ex


async def get_auth_user_info(token_payload: dict = Depends(get_auth_token_payload)) -> SAuthUserInfo:
    """
    Получение информации о пользователе из токена
    """

    try:
        # проверка типа токена
        if token_payload.get("type") != JWT_TYPE_ACCESS:
            raise TokenTypeErrorEx

        return SAuthUserInfo(
            id=token_payload.get("id"),
            name=token_payload.get("name"),
            email=token_payload.get("email"),
            roles=token_payload.get("roles"),
        )

    except TokenTypeErrorEx:
        raise unauthorized_401

    except Exception as ex:
        logger.exception(ex)
        raise Exception from ex


async def get_auth_user_id(token_payload: dict = Depends(get_auth_token_payload)) -> int:
    """
    Получение id текущего аутентифицированного пользователя из access-токена в заголовках
    """

    try:
        # проверка типа токена
        if token_payload.get("type") != JWT_TYPE_ACCESS:
            raise TokenTypeErrorEx

        return token_payload.get("id")

    except TokenTypeErrorEx:
        raise unauthorized_401

    except (ValueError, Exception) as ex:
        logger.exception(ex)
        raise Exception from ex


async def get_auth_user_roles(token_payload: dict = Depends(get_auth_token_payload)) -> list:
    """
    Получение ролей авторизованного пользователя
    """

    try:
        return token_payload.get("roles", [])

    except (ValueError, Exception) as ex:
        raise AuthRoleErrorEx from ex


async def get_auth_admin_id(
        user_id: int = Depends(get_auth_user_id),
        roles: list = Depends(get_auth_user_roles)
) -> int:
    """
    Получение id авторизованного администратора
    """

    try:
        if "admin" not in roles:
            raise AuthRoleErrorEx

        return user_id

    except AuthRoleErrorEx:
        raise unauthorized_403

    except (ValueError, Exception) as ex:
        logger.exception(ex)
        raise Exception from ex


async def get_auth_editor_id(
        user_id: int = Depends(get_auth_user_id),
        roles: list = Depends(get_auth_user_roles)
) -> int:
    """
    Получение id авторизованного редактора
    """

    try:
        if "editor" not in roles and "admin" not in roles:
            raise AuthRoleErrorEx

        return user_id

    except AuthRoleErrorEx:
        raise unauthorized_403

    except (ValueError, Exception) as ex:
        logger.exception(ex)
        raise Exception from ex


async def get_auth_moderator_id(
        user_id: int = Depends(get_auth_user_id),
        roles: list = Depends(get_auth_user_roles)
) -> int:
    """
    Получение id авторизованного модератора
    """

    try:
        if "moderator" not in roles and "admin" not in roles:
            raise AuthRoleErrorEx

        return user_id

    except AuthRoleErrorEx:
        raise unauthorized_403

    except (ValueError, Exception) as ex:
        logger.exception(ex)
        raise Exception from ex


DAuthToken = Annotated[str, Depends(get_auth_token)]
DAuthUserInfo = Annotated[SAuthUserInfo, Depends(get_auth_user_info)]
DAuthUserId = Annotated[int, Depends(get_auth_user_id)]
DAuthAdminId = Annotated[int, Depends(get_auth_admin_id)]
DAuthEditorId = Annotated[int, Depends(get_auth_editor_id)]
DAuthModeratorId = Annotated[int, Depends(get_auth_moderator_id)]
