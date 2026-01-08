from app.domain.entities.script import Script
from app.domain.entities.enums import ScriptStatus
from app.domain.uow.unit_of_work import UnitOfWork
from app.infrastructure.celery.tasks.process_scripts import process_script_task
from app.application.exceptions.exception import ScriptValidationError, ScriptPersistenceError, ScriptProcessingDispatchError


class CreateScriptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, *, script_id: str, name: str, content: str, tags: list[str]) -> Script:

        # ---------- Validation ----------
        if not name:
            raise ScriptValidationError("Script name is required")

        if not content:
            raise ScriptValidationError("Script content is required")

        if not isinstance(tags, list):
            raise ScriptValidationError("Tags must be a list")

        # ---------- Persistence ----------
        try:
            async with self.uow:
                script = Script(
                    id=script_id,
                    name=name,
                    content=content,
                    tags=tags,
                    status=ScriptStatus.PENDING,
                )

                await self.uow.scripts.save(script)
                await self.uow.commit()

        except Exception as exc:
            await self.uow.rollback()
            raise ScriptPersistenceError(
                "Failed to persist script"
            ) from exc

        # ---------- Background Processing ----------
        try:
             process_script_task.delay(
                script.id,
                script.name,
                script.content,
                script.tags
            )
        except Exception as exc:
            # Script is saved, but background task failed
            raise ScriptProcessingDispatchError(
                "Script created but processing could not be started"
            ) from exc

        return script
