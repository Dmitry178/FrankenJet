import aiohttp
import json
import jwt
import secrets
import urllib.parse

from aiohttp import ContentTypeError
from typing import Dict

from app.api.types import ABody
from app.core.config import settings
from app.core.config_const import OAUTH2_GOOGLE_URL, OAUTH2_GOOGLE_TOKEN_URL, OAUTH2_GOOGLE_REDIRECT_URL


class OAuth2Services:

    class Google:
        @staticmethod
        async def get_oauth2_redirect_url():
            """
            Генерация URL перенаправления для Google-аутентификации
            """

            random_state = secrets.token_urlsafe(16)
            query_params = {
                "client_id": settings.OAUTH2_GOOGLE_CLIENT_ID,
                "redirect_uri": OAUTH2_GOOGLE_REDIRECT_URL,
                "response_type": "code",
                "scope": "openid profile email",
                # "access_type": "offline",  # по умолчанию online
                "state": random_state,
            }
            query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)

            return f"{OAUTH2_GOOGLE_URL}?{query_string}"

        @staticmethod
        async def get_oauth2_user_info(code: ABody, state: ABody) -> Dict:
            """
            Получение данных о пользователе
            """

            data = {
                "client_id": settings.OAUTH2_GOOGLE_CLIENT_ID,
                "client_secret": settings.OAUTH2_GOOGLE_CLIENT_SECRET,
                "redirect_uri": OAUTH2_GOOGLE_REDIRECT_URL,
                "grant_type": "authorization_code",
                "code": code,
            }

            # TODO: вынести сессию
            async with aiohttp.ClientSession() as session, session.post(
                    url=OAUTH2_GOOGLE_TOKEN_URL, data=data, ssl=False
            ) as response:

                if response.status != 200:
                    # error_text = await response.text()
                    raise  # TODO: добавить вызов кастомной ошибки

                # Проверка content-type
                content_type = response.headers.get('content-type', '')
                if 'application/json' not in content_type:
                    # error_text = await response.text()
                    raise  # TODO: добавить вызов кастомной ошибки

                try:
                    result = await response.json()

                    id_token = result.get("id_token")
                    # access_token = result.get("access_token")
                    user_data = jwt.decode(
                        id_token,
                        algorithms=["RS256"],
                        options={"verify_signature": False},
                    )

                except (ContentTypeError, json.JSONDecodeError) as ex:
                    # error_text = await response.text()
                    raise  # TODO: добавить вызов кастомной ошибки

                # Дополнительная проверка на ошибки Google OAuth
                if 'error' in result:
                    raise  # TODO: добавить вызов кастомной ошибки

            # TODO: переделать в pydantic-схему
            ret = {
                "fullname": user_data.get("name"),
                "name": user_data.get("given_name"),
                "family": user_data.get("family_name"),
                "email": user_data.get("email"),
                "picture": user_data.get("picture"),
            }

            return ret
