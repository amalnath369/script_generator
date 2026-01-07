from datetime import datetime
from uuid import uuid4

from app.domain.entities.generated_script import GeneratedScript
from app.domain.uow.unit_of_work import UnitOfWork
from app.application.exceptions.exception import GeneratedScriptValidationError, GeneratedScriptPersistenceError


class CreateGeneratedScriptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, *, script_id: str, content: str, model_name: str) -> GeneratedScript:

        # ---------- Validation ----------
        if not script_id:
            raise GeneratedScriptValidationError("script_id is required")

        if not content:
            raise GeneratedScriptValidationError("generated content cannot be empty")

        if not model_name:
            raise GeneratedScriptValidationError("model_name is required")

        generated = GeneratedScript(
            id=str(uuid4()),
            script_id=script_id,
            content=content,
            model_name=model_name,
            created_at=datetime.utcnow(),
        )

        # ---------- Persistence ----------
        try:
            async with self.uow:
                await self.uow.generated_scripts.save(generated)
                await self.uow.commit()

        except Exception as exc:
            await self.uow.rollback()
            raise GeneratedScriptPersistenceError(
                "Failed to save generated script"
            ) from exc

        return generated
