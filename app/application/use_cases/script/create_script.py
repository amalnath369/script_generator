from app.domain.entities.script import Script
from app.domain.entities.enums import ScriptStatus
from app.domain.uow.unit_of_work import UnitOfWork
from app.infrastructure.celery.tasks.process_scripts import  process_script_task



class CreateScriptUseCase:
    """
    Use case responsible for:
    - Creating a Script domain entity
    - Persisting it atomically using Unit of Work
    - Triggering background LLM processing via Celery
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(
        self,
        *,
        script_id: str,
        name: str,
        content: str,
        tags: list[str],
    ) -> Script:

        async with self.uow:
            # 1️⃣ Create domain entity
            script = Script(
                id=script_id,
                name=name,
                content=content,
                tags=tags,
                status=ScriptStatus.PENDING,
            )

            # 2️⃣ Persist using repository via UoW
            await self.uow.scripts.save(script)

        # 3️⃣ Trigger background processing AFTER commit
        process_script_task.delay(script.id)

        return script