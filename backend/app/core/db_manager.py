""" Контекстный менеджер базы данных """

from sqlalchemy.exc import IllegalStateChangeError

from app.core.logs import logger
from app.db.repository.aircraft import AircraftRepository
from app.db.repository.articles import ArticlesRepository
from app.db.repository.auth import RefreshTokensRepository
from app.db.repository.chatbot import ChatBotSettingsRepository, ChatBotHistoryRepository
from app.db.repository.knowledge_base import ProjectKnowledgeRepository
from app.db.repository.countries import CountriesRepository
from app.db.repository.facts import FactsRepository
from app.db.repository.roles import RolesRepository, UserRolesRepository
from app.db.repository.tags import TagsRepository
from app.db.repository.users import UsersRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    class AuthDBManager:
        """
        Менеджер БД авторизации/аутентификации
        """

        def __init__(self, session):
            self.session = session

            self.refresh_tokens = RefreshTokensRepository(self.session)
            self.roles = RolesRepository(self.session)
            self.user_roles = UserRolesRepository(self.session)

    class AppDBManager:
        """
        Менеджер БД репозиториев схемы app
        """

        def __init__(self, session):
            self.session = session

            self.project_knowledge = ProjectKnowledgeRepository(self.session)

    class ChatBotDBManager:
        """
        Менеджер БД репозиториев чат-бота
        """

        def __init__(self, session):
            self.session = session

            self.settings = ChatBotSettingsRepository(self.session)
            self.history = ChatBotHistoryRepository(self.session)

    async def __aenter__(self):
        self.session = self.session_factory()

        self.app = self.AppDBManager(self.session)
        self.auth = self.AuthDBManager(self.session)
        self.chatbot = self.ChatBotDBManager(self.session)

        self.aircraft = AircraftRepository(self.session)
        self.articles = ArticlesRepository(self.session)
        self.countries = CountriesRepository(self.session)
        self.facts = FactsRepository(self.session)
        self.tags = TagsRepository(self.session)
        self.users = UsersRepository(self.session)

        return self

    async def __aexit__(self, exc_type, *_):  # exc_val, exc_tb
        try:
            # if exc_type is not None:
            #     # откатываем транзакция при except
            #     await self.session.rollback()
            await self.session.rollback()
        finally:
            try:
                await self.session.close()
            except IllegalStateChangeError:
                # Игнорируем ошибку состояния, так как сессия уже закрывается или находится в промежуточном состоянии
                pass
            except Exception as ex:
                logger.exception(f"Error closing session", extra={"error": str(ex)})

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
        await self.session.close()
