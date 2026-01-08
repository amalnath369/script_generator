from app.domain.entities.generated_script import GeneratedScript
from app.domain.uow.unit_of_work import UnitOfWork
from app.application.exceptions.exception import GeneratedScriptNotFoundError



class DeleteGenerateScriptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, *, generated_script_id: str) -> None:
        async with self.uow:
            result = await self.uow.generated_scripts.get_by_id(generated_script_id)

        if not result:
            raise GeneratedScriptNotFoundError(f"Generated script with id {generated_script_id} not found")

        async with self.uow:
            await self.uow.generated_scripts.delete(generated_script_id)