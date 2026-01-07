from app.domain.entities.script import Script
from app.domain.uow.unit_of_work import UnitOfWork

from app.application.exceptions.exception import ScriptNotFoundError


class DeleteScriptsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, *, script_id: str) -> None:
        async with self.uow:
            script = await self.uow.scripts.get_by_id(script_id)
            if script is None:
                raise ScriptNotFoundError(f"Script with id {script_id} not found.")

            await self.uow.scripts.delete(script_id)