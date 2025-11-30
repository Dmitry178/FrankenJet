from app.config.env import settings
from app.core import chatbot_settings


class AppServices:

    @staticmethod
    async def get_settings() -> dict:
        """
        Настройки приложения
        """

        # список доступных способов аутентификации
        auth_methods = {
            "authentication": settings.ALLOW_AUTHENTICATION,
            "registration": settings.ALLOW_REGISTRATION,
            "reset_password": settings.ALLOW_RESET_PASSWORD,
            "oauth2_google": (
                    settings.ALLOW_OAUTH2_GOOGLE
                    and bool(settings.OAUTH2_GOOGLE_CLIENT_ID)
                    and bool(settings.OAUTH2_GOOGLE_CLIENT_SECRET)
            ),
            "oauth2_vk": (
                    settings.ALLOW_OAUTH2_VK
                    and bool(settings.OAUTH2_VK_CLIENT_ID)
                    and bool(settings.OAUTH2_VK_CLIENT_SECRET)
            ),
        }

        # пути
        urls = {
            "images": settings.S3_DIRECT_URL,  # путь к S3-хранилищу
        }

        if settings.GIGACHAT_AUTH_KEY and settings.GIGACHAT_SCOPE:
            await chatbot_settings.initialize()
            chat_bot = chatbot_settings.get("enabled")
        else:
            chat_bot = False

        return {
            "auth_methods": auth_methods,  # доступные методы аутентификации
            "urls": urls,  # пути к сервисам
            "chat_bot": chat_bot,  # включен ли чат-бот
        }
