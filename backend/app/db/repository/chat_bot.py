from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from uuid import UUID

from app.db.models import ChatBotSettings, ChatHistory
from app.db.models.chat_bot import MessageIntent
from app.db.repository.base import BaseEmptyRepository, BaseRepository
from app.schemas.chat_bot import SChatBotSettings


class ChatBotHistoryRepository(BaseRepository):
    """
    Репозиторий модели истории чат-бота
    """

    model = ChatHistory

    async def get_user_history(self, chat_id: UUID, api: bool, limit=20):
        """
        Получение истории чата
        """

        query = (
            select(ChatHistory.message, ChatHistory.answer, ChatHistory.created_at)
            .where(
                ChatHistory.chat_id == chat_id,
                ChatHistory.answer.is_not(None),
                ChatHistory.is_active.is_(True)
            )
            .limit(limit)
            .order_by(ChatHistory.created_at.desc())
        )

        if api:
            query = (
                query
                .where(
                    ChatHistory.intent == str(MessageIntent.intent_ontopic)
                )
            )

        return (await self.session.execute(query)).mappings().all()

    async def put_message(self, **values) -> int:
        """
        Добавление сообщения пользователя
        """

        stmt = (
            insert(ChatHistory)
            .values(**values)
            .returning(ChatHistory.id)
        )

        result = await self.session.execute(stmt)
        return result.scalar()


class ChatBotSettingsRepository(BaseEmptyRepository):
    """
    Репозиторий настроек чат-бота
    """

    model = ChatBotSettings

    async def get_settings(self):
        """
        Чтение настроек чат-бота
        """

        query = select(ChatBotSettings).limit(1)
        return (await self.session.execute(query)).scalars().one_or_none()

    async def update_settings(self, settings: SChatBotSettings):
        """
        Запись настроек чат-бота
        """

        index_elements = ["id"]
        values = settings.model_dump(exclude_unset=True)
        set_ = {key: text(f"EXCLUDED.{key}") for key in values.keys()}
        values["id"] = 1

        stmt = (
            insert(ChatBotSettings)
            .values(**values)
            .on_conflict_do_update(
                index_elements=index_elements,
                set_=set_
            )
            .returning(ChatBotSettings)
        )

        return (await self.session.execute(stmt)).mappings().one_or_none()
