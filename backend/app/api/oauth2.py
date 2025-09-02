from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import RedirectResponse

from app.dependencies.db import DDB
from app.exceptions.oauth2 import OAuth2ErrorEx
from app.services.auth import AuthServices
from app.services.oauth2 import OAuth2Services
from app.services.users import UsersServices
from app.types import ABody, status_ok

oauth_router = APIRouter(prefix="/oauth", tags=["Auth"])


@oauth_router.get("/google")
async def get_google_oauth2_redirect():
    """
    Генерация перенаправления для Google-аутентификации
    """

    url = await OAuth2Services.Google.get_oauth2_redirect_url()
    return RedirectResponse(url=url, status_code=302)


@oauth_router.post("/google/redirect")
async def process_google_callback(code: ABody, state: ABody, db: DDB):
    """
    Обработка ответа от Google
    """

    try:
        # TODO: убрать дублирование кода, сделать через провайдеров oauth2
        user_data = await OAuth2Services.Google.get_oauth2_user_data(code, state)
        user = await UsersServices(db).get_or_create_user_by_oauth2(user_data)
        tokens = await AuthServices(db).issue_tokens(user.id, user.email, user.roles)
        return {**status_ok, "data": tokens.model_dump()}

    except OAuth2ErrorEx as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)

    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ex))


@oauth_router.get("/vk")
async def get_vk_oauth2_redirect():
    """
    Генерация перенаправления для VK-аутентификации
    """

    url = await OAuth2Services.VK.get_oauth2_redirect_url()
    return RedirectResponse(url=url, status_code=302)


@oauth_router.post("/vk/redirect")
async def process_google_callback(code: ABody, state: ABody, db: DDB):
    """
    Обработка ответа от VK
    """

    try:
        # TODO: убрать дублирование кода, сделать через провайдеров oauth2
        user_data = await OAuth2Services.VK.get_oauth2_user_data(code, state)
        user = await UsersServices(db).get_or_create_user_by_oauth2(user_data)
        tokens = await AuthServices(db).issue_tokens(user.id, user.email, user.roles)
        return {**status_ok, "data": tokens.model_dump()}

    except OAuth2ErrorEx as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)

    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ex))
