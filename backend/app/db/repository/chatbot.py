from sqlalchemy import select, text, func
from sqlalchemy.dialects.postgresql import insert
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.db.models import ChatBotSettings, Chat
from app.db.repository.base import BaseEmptyRepository, BaseRepository
from app.schemas.chatbot import SChatBotSettings


class ChatBotHistoryRepository(BaseRepository):
    """
    Репозиторий модели истории чат-бота
    """

    model = Chat

    async def get_user_history(self, chat_id: UUID, intent: str | None = None, limit=20):
        """
        Получение истории чата
        """

        query = (
            select(Chat.message, Chat.answer, Chat.created_at)
            .where(
                Chat.chat_id == chat_id,
                Chat.answer.is_not(None),
                Chat.is_active.is_(True)
            )
            .limit(limit)
            .order_by(Chat.created_at.desc())
        )

        if intent:
            query = query.where(Chat.intent == intent)

        return (await self.session.execute(query)).mappings().all()

    async def count_daily_tokens(self, chat_id: UUID) -> dict[str, int]:
        """
        Подсчёт токенов, потраченных за день
        """

        query = select(
            func.sum(
                Chat.total_tokens + Chat.precached_prompt_tokens
            ).filter(Chat.chat_id == chat_id).label("user_daily_tokens"),
            func.sum(
                Chat.total_tokens + Chat.precached_prompt_tokens
            ).label("total_daily_tokens")
        ).where(
            func.date(Chat.created_at) == func.date(func.now()),  # noqa
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
            insert(Chat)
            .values(**values)
            .returning(Chat.id)
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

    async def update_settings(self, settings: SChatBotSettings, exclude_unset=False, commit=False):
        """
        Запись настроек чат-бота
        """

        index_elements = ["id"]
        values = settings.model_dump(exclude_unset=exclude_unset)
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

        if commit:
            await self.session.commit()

        return (await self.session.execute(stmt)).scalars().one_or_none()
