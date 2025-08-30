import aiohttp
import base64
import hashlib
import json
import jwt
import secrets
import urllib.parse

from aiohttp import ContentTypeError
from typing import Dict

from app.core.config import settings
from app.core.config_const import OAUTH2_GOOGLE_URL, OAUTH2_GOOGLE_TOKEN_URL, OAUTH2_GOOGLE_REDIRECT_URL, \
    OAUTH2_VK_URL, OAUTH2_VK_REDIRECT_URL, OAUTH2_VK_TOKEN_URL
from app.types import ABody


class OAuth2Services:

    @staticmethod
    async def generate_code_verifier(length: int = 64) -> str:
        """
        Генерация случайной строки code_verifier
        """

        token = secrets.token_urlsafe(length)
        # длина строки token должна быть кратной 4 для корректной работы base64url
        while len(token) % 4 != 0:
            token += '='

        # обрезаем до необходимой длины, т.к. secrets.token_urlsafe может вернуть строку, превышающую запрошенную длину
        return token[:length]

    @staticmethod
    async def generate_code_challenge(code_verifier: str) -> str:
        """
        Генерация строки code_challenge из code_verifier, используя метод S256
        """

        code_verifier_bytes = code_verifier.encode('ascii')
        hashed = hashlib.sha256(code_verifier_bytes).digest()
        encoded = base64.urlsafe_b64encode(hashed).decode('ascii').rstrip('=')

        return encoded

    class Google:

        @staticmethod
        async def get_oauth2_redirect_url():
            """
            Генерация URL перенаправления для Google OAuth2-аутентификации
            """

            state = secrets.token_urlsafe(16)  # TODO: сделать хранение state в базе
            query_params = {
                "client_id": settings.OAUTH2_GOOGLE_CLIENT_ID,
                "redirect_uri": OAUTH2_GOOGLE_REDIRECT_URL,
                "response_type": "code",
                "scope": "openid profile email",
                # "access_type": "offline",  # по умолчанию online
                "state": state,
            }
            query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)

            return f"{OAUTH2_GOOGLE_URL}?{query_string}"

        @staticmethod
        async def get_oauth2_user_info(code: ABody, state: ABody) -> Dict:
            """
            Получение данных о пользователе
            """

            # TODO: сделать проверку state из базы

            data = {
                "client_id": settings.OAUTH2_GOOGLE_CLIENT_ID,
                "client_secret": settings.OAUTH2_GOOGLE_CLIENT_SECRET,
                "redirect_uri": OAUTH2_GOOGLE_REDIRECT_URL,
                "grant_type": "authorization_code",
                "code": code,
            }

            # TODO: сделать менеджер сессий
            async with aiohttp.ClientSession() as session, session.post(
                    url=OAUTH2_GOOGLE_TOKEN_URL, data=data, ssl=False  # TODO: убрать ssl=False при production
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
                    # refresh_token = result.get("refresh_token")
                    user_data = jwt.decode(
                        id_token,
                        algorithms=["RS256"],
                        options={"verify_signature": False},  # TODO: сделать запрос public key для проверки токена
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

    class VK:

        @staticmethod
        async def get_oauth2_redirect_url():
            """
            Генерация URL перенаправления для VK OAuth2-аутентификации
            """

            state = secrets.token_urlsafe(16)

            # параметры, необходимые для OAuth 2.0 с PKCE (онлайн-генератор https://tonyxu-io.github.io/pkce-generator/)
            code_verifier = await OAuth2Services.generate_code_verifier()
            code_challenge = await OAuth2Services.generate_code_challenge(code_verifier)
            # TODO: сделать хранение значений в базе для дальнейшей проверки

            query_params = {
                "client_id": settings.OAUTH2_VK_CLIENT_ID,
                "redirect_uri": OAUTH2_VK_REDIRECT_URL,
                "response_type": "code",
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "scope": "email",  # phone vkid.personal_info (по умолчанию)
                # "lang_id": 3,  # RUS = 0 (по умолчанию), ENG = 3
                # "scheme": "dark",  # light (по умолчанию), dark
            }
            query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)

            return f"{OAUTH2_VK_URL}?{query_string}"
