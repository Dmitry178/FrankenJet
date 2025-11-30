"""
Контекстный менеджер для работы с GigaChat API

Документация по GigaChat API
https://github.com/ai-forever/gigachat
"""

import aiohttp
import requests

from datetime import datetime
from uuid import UUID, uuid4

import urllib3

from app.config.chat_bot import ChatBotSettingsManager
from app.config.env import settings
from app.core import chatbot_settings
from app.schemas.gigachat import SGigaChatAnswer


class GigaChatAPIError(Exception):
    """
    Базовое исключение для API GigaChat
    """

    pass


class GigaChatAuthenticationError(GigaChatAPIError):
    """
    Ошибка аутентификации (401, 403)
    """

    pass


class GigaChatTokenExpiredError(GigaChatAPIError):
    """
    Ошибка авторизации (токен истёк) (401)
    """

    pass


class GigaChatPaymentRequiredError(GigaChatAPIError):
    """
    Ошибка, связанная с необходимостью оплаты (402)
    """

    pass


class GigaChatRequestError(GigaChatAPIError):
    """
    Общая ошибка запроса (4xx, 5xx)
    """

    pass


class GigaChatAPIContextManager:
    def __init__(self, auth_token: UUID, scope: str, chatbot_settings_manager: ChatBotSettingsManager):

        self.chatbot_settings_manager = chatbot_settings_manager  # менеджер настроек бота
        self.chatbot_enabled: bool | None = None  # активирован ли чат-бот
        self.auth_token = auth_token  # токен аутентификации
        self.token = None  # токен авторизации
        self.system_prompt: str | None = None  # системный промт
        self.scope = scope  # scope api
        self.model: str | None = None  # название модели
        self.expires_at: int | None = None  # время истечения токена

        self.session = None  # http-сессия
        self.headers = None  # заголовки

        self.payment_required = True
        self.initialized = False

        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.completion_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    async def __aenter__(self):
        if not self.auth_token:
            return

        # создание сессии
        connector = aiohttp.TCPConnector(verify_ssl=False)
        self.session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self.auth_token:
            return

        if self.session and not self.session.closed:
            await self.session.close()

    def set_headers(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def init_settings(self):
        """
        Загрузка настроек
        """

        await self.chatbot_settings_manager.initialize()
        self.chatbot_enabled = self.chatbot_settings_manager.get("enabled", False)
        self.system_prompt = self.chatbot_settings_manager.get("system_prompt")
        self.model = self.chatbot_settings_manager.get("model")
        self.initialized = True

    async def authenticate(self):
        """
        Аутентификация и получение токена
        """

        if not self.auth_token:
            return

        if not self.initialized:
            await self.init_settings()

        if not self.chatbot_enabled:
            return

        payload = {
            "scope": self.scope,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid4()),
            "Authorization": f"Basic {self.auth_token}"
        }

        # TODO: перевести на aiohttp, либо gigachat sdk
        # async with self.session.post(self.auth_url, headers=headers, json=payload) as response:

        try:
            response = requests.request("POST", self.auth_url, headers=headers, data=payload, verify=False)

            if response.status_code == 402:
                self.payment_required = True
                raise GigaChatPaymentRequiredError("Закончилась оплата")
            elif response.status_code == 401 or response.status_code == 403:
                raise GigaChatAuthenticationError("Ошибка авторизации/аутентификации")
            elif response.status_code >= 400:
                print(response.text)
                raise GigaChatRequestError("Ошибка запроса к GigaChat")

            data = response.json()  # await для aiohttp
            self.token = data.get("access_token")
            self.expires_at = data.get("expires_at")

            return True

        except Exception as ex:
            print(ex)
            self.token = None
            self.expires_at = None
            return False

    def is_token_expired(self) -> bool | None:
        """
        Проверка, истёк ли токен авторизации
        """

        if not self.auth_token:
            return None

        return not self.expires_at or datetime.now().timestamp() >= self.expires_at

    def is_authenticated(self) -> bool:
        """
        Проверка аутентификации
        """

        if not self.auth_token:
            return False

        return self.token is not None and not self.is_token_expired()

    async def send_message(self, message: str, history=None):
        """
        Отправка сообщение в модель LLM
        """

        if not message:
            return None

        if not self.initialized:
            await self.init_settings()

        if not self.chatbot_enabled:
            return None

        if self.is_token_expired():
            if not await self.authenticate():
                return None

        reason_mapping = {
            "blacklist": "intent_blacklist",
            "timeout": "intent_timeout",
        }

        # подготовка истории сообщений
        messages = [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []
        if history and isinstance(history, list):
            messages.extend(history)

        # добавление сообщения пользователя
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "update_interval": 0
        }

        max_retries = 3
        for attempt in range(max_retries-1):
            # TODO: перевести на aiohttp
            # async with self.session.post(self.completion_url, headers=headers, json=payload, ssl=False) as response:

            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}"
            }

            response = requests.request("POST", self.completion_url, headers=headers, json=payload, verify=False)

            if response.status_code == 200:
                data = response.json()  # await для aiohttp

                finish_reason = data["choices"][0].get("finish_reason") or ""
                answer = reason_mapping.get(finish_reason, data["choices"][0]["message"]["content"])

                return SGigaChatAnswer(
                    answer=answer,
                    prompt_tokens=data.get("usage", []).get("prompt_tokens"),
                    completion_tokens=data.get("usage", []).get("completion_tokens"),
                    total_tokens=data.get("usage", []).get("total_tokens"),
                    precached_prompt_tokens=data.get("usage", []).get("precached_prompt_tokens"),
                )

            elif response.status_code == 401:
                if not await self.authenticate():
                    raise GigaChatAuthenticationError("Ошибка аутентификации")
                continue

            elif response.status_code == 402:
                self.payment_required = True
                raise GigaChatPaymentRequiredError("Закончилась оплата")

            elif response.status_code >= 400:
                error_text = response.text
                raise GigaChatRequestError(f"Ошибка запроса к GigaChat: {response.status_code} - {error_text}")

        raise GigaChatRequestError(f"Все попытки отправки сообщения исчерпаны ({max_retries}).")


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
gigachat_api = GigaChatAPIContextManager(
    auth_token=settings.GIGACHAT_AUTH_KEY,
    scope=settings.GIGACHAT_SCOPE,
    chatbot_settings_manager=chatbot_settings,
)
