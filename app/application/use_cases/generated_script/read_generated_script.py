from app.domain.entities.generated_script import GeneratedScript
from app.domain.uow.unit_of_work import UnitOfWork
from app.application.exceptions.exception import GeneratedScriptNotFoundError


class ReadGeneratedScriptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, *, generated_script_id: str) -> GeneratedScript:
        async with self.uow:
            result = await self.uow.generated_scripts.get(generated_script_id)

        if not result:
            raise GeneratedScriptNotFoundError(f"Generated script with id {generated_script_id} not found")

        return result
