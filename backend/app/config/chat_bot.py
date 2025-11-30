from typing import Any

from app.core.db_manager import DBManager
from app.core.logs import logger
from app.db import async_session_maker
from app.schemas.chat_bot import SChatBotSettings


class ChatBotSettingsManager:
    """
    Менеджер настроек чат-бота
    """

    def __init__(self):
        self.db_manager = DBManager(session_factory=async_session_maker)
        self._settings: SChatBotSettings | None = None
        self.initialized = False

    async def initialize(self):
        """
        Загрузка настроек из базы данных при инициализации приложения
        """

        if self.initialized:
            return

        try:
            async with self.db_manager as db:
                settings = await db.chatbot.settings.get_settings()
                settings_dict = {
                    column.name: getattr(settings, column.name)
                    for column in settings.__table__.columns
                }
                self._settings = SChatBotSettings(**settings_dict)
                self.initialized = True

        except Exception as ex:
            logger.error(f"Ошибка загрузки настроек: {ex}")
            raise ex

    @property
    def settings(self) -> SChatBotSettings:
        """
        Настройки
        """

        if not self.initialized:
            raise RuntimeError("Настройки не загружены")

        return self.settings

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
            async with self.db_manager as db:
                await db.chatbot.settings.update_settings(settings)
                await db.commit()

            self._settings = settings

        except Exception as ex:
            logger.error(f"Ошибка обновления настроек: {ex}")
            raise ex
