from app.domain.entities.script import Script
from app.domain.uow.unit_of_work import UnitOfWork



class UpdateScriptsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, *, script_id: str, name: str, content: str, tags: list[str]) -> Script:
        async with self.uow:
            script = await self.uow.scripts.get_by_id(script_id)
            if script is None:
                raise ValueError(f"Script with id {script_id} not found.")

            updated_script = Script(
                id=script.id,
                name=name,
                content=content,
                tags=tags,
                status=script.status
            )

            await self.uow.scripts.update(updated_script)
            return updated_script