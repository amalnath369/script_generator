from app.domain.entities.script import Script
from app.domain.uow.unit_of_work import UnitOfWork



class ReadScriptsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, * , script_id: str) -> Script:
        async with self.uow:
            script = await self.uow.scripts.get_by_id(script_id)

            if script is None:
                raise ValueError(f"Script with id {script_id} not found.")
            return script