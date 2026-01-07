from typing import List
from app.domain.entities.script import Script
from app.domain.uow.unit_of_work import UnitOfWork


class ListAllScriptsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self) -> List[Script]:
        async with self.uow:
            scripts = await self.uow.scripts.list_all()
            return scripts