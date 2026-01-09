from app.config.chatbot import ChatBotSettingsManager
from app.core.db_manager import DBManager
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.chatbot import SChatBotSettings


class ChatBotSettingsServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def get_settings(self) -> SChatBotSettings:
        """
        Чтение настроек AI/RAG-бота
        """

        return await self.db.chatbot.settings.get_settings()

    @handle_basic_db_errors
    async def update_settings(
            self,
            settings: SChatBotSettings,
            chatbot_settings: ChatBotSettingsManager,
            exclude_unset=False
    ):
        """
        Обновление настроек AI/RAG-бота
        """

        result = await self.db.chatbot.settings.update_settings(settings, exclude_unset=exclude_unset, commit=True)
        await chatbot_settings.update_bot_settings(settings, exclude_unset)
        return result
