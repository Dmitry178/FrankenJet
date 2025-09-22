from uuid import UUID

from app.db.db_manager import DBManager


class FactsServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def get_random_facts(self, num: int = 3):
        """
        Получение случайных фактов
        """

        return await self.db.facts.get_random_facts(num)

    async def add_fact(self, fact: str):
        """
        Добавление факта
        """

        return await self.db.facts.insert_one(fact=fact)

    async def edit_fact(self, fact_id: UUID, fact: str):
        """
        Редактирование факта
        """

        return await self.db.facts.update_one(id=fact_id, fact=fact, commit=True)

    async def delete_fact(self, fact_id: int):
        """
        Удаление факта
        """

        return await self.db.facts.delete_one(id=fact_id)
