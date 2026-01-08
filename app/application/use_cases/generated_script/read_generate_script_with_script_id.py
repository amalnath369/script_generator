from app.domain.entities.generated_script import GeneratedScript
from app.domain.uow.unit_of_work import UnitOfWork
from app.application.exceptions.exception import GeneratedScriptNotFoundError



class ReadGenerateScriptWithScriptIdUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, *, script_id: str) -> GeneratedScript:
        async with self.uow:
            result = await self.uow.generated_scripts.get_by_script_id(script_id)

        if not result:
            raise GeneratedScriptNotFoundError(f"Generated script with script id {script_id} not found")

        return result