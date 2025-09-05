from app.core.config_env import settings


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

        return {
            "auth_methods": auth_methods,
        }
