from app.db.repository.aircraft import AircraftRepository, CountriesRepository, DesignersRepository, \
    ManufacturersRepository, DesignBureausRepository
from app.db.repository.articles import ArticlesRepository
from app.db.repository.auth import RefreshTokensRepository
from app.db.repository.users import UsersRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    class AuthDBManager:
        def __init__(self, session):
            self.session = session

            self.refresh_tokens = RefreshTokensRepository(self.session)

    class AircraftDBManager:
        def __init__(self, session):
            self.session = session

            self.aircraft = AircraftRepository(self.session)
            self.countries = CountriesRepository(self.session)
            self.design_bureaus = DesignBureausRepository(self.session)
            self.designers = DesignersRepository(self.session)
            self.manufacturers = ManufacturersRepository(self.session)

    async def __aenter__(self):
        self.session = self.session_factory()

        self.aircraft = self.AircraftDBManager(self.session)
        self.auth = self.AuthDBManager(self.session)

        self.articles = ArticlesRepository(self.session)
        self.users = UsersRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
        await self.session.close()
