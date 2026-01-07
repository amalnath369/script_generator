from typing import Type

from app.domain.uow.unit_of_work import UnitOfWork
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.repositories.script_repo import IScriptRepository
from app.infrastructure.repositories.generate_script_repo import IGeneratedScriptRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self):
        self._session_factory = AsyncSessionLocal
        self.session = None

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()

        # bind repositories to the SAME session
        self.scripts = IScriptRepository(self.session)
        self.generated_scripts = IGeneratedScriptRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.rollback()
        else:
            await self.commit()

        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
