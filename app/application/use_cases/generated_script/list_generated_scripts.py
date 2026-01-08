from typing import List
from app.domain.entities.generated_script import GeneratedScript
from app.domain.uow.unit_of_work import UnitOfWork


class ListGeneratedScriptsByScriptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, *, limit: int, offset: int) -> List[GeneratedScript]:
        async with self.uow:
            total, scripts = await self.uow.scripts.list_all(
                limit=limit,
                offset=offset
            )
            return total, scripts