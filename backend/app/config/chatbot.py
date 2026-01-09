from typing import Any

from app.core.db_manager import DBManager
from app.core.logs import logger
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

    @staticmethod
    async def get_bot_settings(db: DBManager) -> SChatBotSettings:
        """
        Чтение настроек бота из базы
        """

        settings = await db.chatbot.settings.get_settings()
        settings_dict = {
            column.name: getattr(settings, column.name)
            for column in settings.__table__.columns
        }
        return SChatBotSettings(**settings_dict)

    async def initialize(self, db: DBManager):
        """
        Загрузка настроек из базы данных при инициализации приложения
        """

        if self.initialized:
            return

        self.db = db

        try:
            self._settings = await self.get_bot_settings(self.db)
            self._chatbot_enabled = self._settings.enabled
            self.initialized = True

        except Exception as ex:
            logger.exception(ex)

    @property
    def bot_enabled(self) -> bool:
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

    async def update_bot_settings(self, settings: SChatBotSettings, exclude_unset=False):
        """
        Обновление настроек, сохранение в базу данных
        """

        if not self.initialized:
            raise RuntimeError("Настройки не загружены")

        if exclude_unset:
            # частичное обновление настроек
            updated_data = settings.model_dump(exclude_unset=True)
            current_settings_dict = self._settings.model_dump()
            current_settings_dict.update(updated_data)
            self._settings = SChatBotSettings(**current_settings_dict)
        else:
            # полное обновление настроек
            self._settings = settings

        self._chatbot_enabled = self._settings.enabled
