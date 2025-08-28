from fastapi import APIRouter
from starlette.responses import RedirectResponse

from app.api.auth.services.oauth import OAuth2Services
from app.api.types import ABody

oauth_router = APIRouter(prefix="/oauth", tags=["Auth"])


@oauth_router.get("/google/url")
async def get_google_oauth2_redirect_url():
    """
    Генерация URL перенаправления для Google-аутентификации
    """

    url = await OAuth2Services.Google.get_oauth2_redirect_url()
    return RedirectResponse(url=url, status_code=302)


@oauth_router.post("/google/callback")
async def process_google_callback(code: ABody, state: ABody):
    """
    Обработка ответа от Google
    """

    # TODO: добавить обработку исключений
    return await OAuth2Services.Google.get_oauth2_user_info(code, state)
