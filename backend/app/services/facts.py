from app.core.db_manager import DBManager
from app.decorators.db_errors import handle_basic_db_errors


class FactsServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @handle_basic_db_errors
    async def add_fact(self, fact: str):
        """
        Добавление факта
        """

        return await self.db.facts.insert_one(fact=fact)

    @handle_basic_db_errors
    async def edit_fact(self, fact_id: int, fact: str):
        """
        Редактирование факта
        """

        return await self.db.facts.update(id=fact_id, fact=fact, commit=True)

    @handle_basic_db_errors
    async def delete_fact(self, fact_id: int):
        """
        Удаление факта
        """

        return await self.db.facts.delete(id=fact_id)
