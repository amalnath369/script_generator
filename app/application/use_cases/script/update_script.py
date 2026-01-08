from typing import Optional, List
from app.domain.entities.script import Script
from app.domain.uow.unit_of_work import UnitOfWork

from app.application.exceptions.exception import ScriptValidationError, ScriptNotFoundError



class UpdateScriptsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, *, script_id: str, name: Optional[str], content: Optional[str], tags: Optional[List[str]]) -> Script:
        async with self.uow:
            script = await self.uow.scripts.get_by_id(script_id)
            if script is None:
                raise ScriptNotFoundError(f"Script with id {script_id} not found.")

            if name is not None:
                script.name = name

            if content is not None:
                script.content = content

            if tags is not None:
                script.tags = tags


            await self.uow.scripts.update(script)
            return script