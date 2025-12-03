from sqlalchemy import select, text, func
from sqlalchemy.dialects.postgresql import insert
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.db.models import ChatBotSettings, ChatHistory
from app.db.models.chatbot import MessageIntent
from app.db.repository.base import BaseEmptyRepository, BaseRepository
from app.schemas.chatbot import SChatBotSettings


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

    async def count_daily_tokens(self, chat_id: UUID) -> dict[str, int]:
        """
        Подсчёт токенов, потраченных за день
        """

        query = select(
            func.sum(
                ChatHistory.total_tokens + ChatHistory.precached_prompt_tokens
            ).filter(ChatHistory.chat_id == chat_id).label("user_daily_tokens"),
            func.sum(
                ChatHistory.total_tokens + ChatHistory.precached_prompt_tokens
            ).label("total_daily_tokens")
        ).where(
            func.date(ChatHistory.created_at) == func.date(func.now()),  # noqa
        )

        result = (await self.session.execute(query)).one_or_none()

        if result is None:
            user_daily_tokens = 0
            total_daily_tokens = 0
        else:
            user_daily_tokens = result.user_daily_tokens or 0
            total_daily_tokens = result.total_daily_tokens or 0

        return {
            "user_daily_tokens": user_daily_tokens,
            "total_daily_tokens": total_daily_tokens,
        }

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

    async def _get_settings(self):
        """
        Чтение настроек чат-бота
        """

        query = select(self.model).limit(1)
        return (await self.session.execute(query)).scalars().one_or_none()

    async def get_settings(self):
        """
        Чтение, либо создание настроек чат-бота
        """

        if result := await self._get_settings():
            return result

        try:
            stmt = insert(self.model).values(id=1).returning(self.model)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalars().one()

        except IntegrityError:
            await self.session.rollback()
            return await self._get_settings()

        except Exception as ex:
            raise ex

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
