from typing import Any

from app.core.db_manager import DBManager
from app.core.logs import logger
from app.db import async_session_maker
from app.schemas.chatbot import SChatBotSettings


class ChatBotSettingsManager:
    """
    Менеджер настроек чат-бота
    """

    def __init__(self):
        self.db = None
        self._chatbot_enabled = False
        self._settings: SChatBotSettings | None = None
        self.initialized = False

    async def initialize(self, db: DBManager):
        """
        Загрузка настроек из базы данных при инициализации приложения
        """

        if self.initialized:
            return

        self.db = db

        try:
            settings = await db.chatbot.settings.get_settings()
            settings_dict = {
                column.name: getattr(settings, column.name)
                for column in settings.__table__.columns
            }
            self._settings = SChatBotSettings(**settings_dict)
            self._chatbot_enabled = self._settings.enabled
            self.initialized = True

        except Exception as ex:
            logger.exception(ex)

    @property
    def enabled(self) -> bool:
        return self._chatbot_enabled

    async def get_settings(self) -> SChatBotSettings:
        """
        Получение настроек чат-бота
        """

        if not self.initialized:
            raise RuntimeError("Настройки не загружены")

        return self._settings

    @property
    def settings(self) -> SChatBotSettings:
        """
        Настройки
        """

        if not self.initialized:
            raise RuntimeError("Настройки не загружены")

        return self._settings

    def get(self, field: str, default: Any = None) -> Any:
        """
        Получение конкретного поля настройки
        """

        if not self.initialized:
            raise RuntimeError("Настройки не загружены")

        return getattr(self._settings, field, default)

    async def update(self, settings: SChatBotSettings):
        """
        Обновление настроек, сохранение в базу данных
        """

        try:
            await self.db.chatbot.settings.update_settings(settings)
            await self.db.commit()
            self._settings = settings
            self._chatbot_enabled = settings.enabled

        except Exception as ex:
            logger.exception(f"Ошибка обновления настроек: {ex}")
            raise ex
