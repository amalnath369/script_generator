from typing import List
from app.domain.entities.generated_script import GeneratedScript
from app.domain.uow.unit_of_work import UnitOfWork


class ListGeneratedScriptsByScriptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, *, script_id: str) -> List[GeneratedScript]:
        async with self.uow:
            return await self.uow.generated_scripts.list_all(script_id)
