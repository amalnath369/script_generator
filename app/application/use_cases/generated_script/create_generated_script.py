from datetime import datetime
from uuid import uuid4
from app.domain.entities.generated_script import GeneratedScript
from app.domain.uow.unit_of_work import UnitOfWork


class CreateGeneratedScriptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(
        self,
        *,
        script_id: str,
        content: str,
        model_name: str,
    ) -> GeneratedScript:
        
        generated = GeneratedScript(
            id=str(uuid4()),
            script_id=script_id,
            content=content,
            model_name=model_name,
            created_at=datetime.utcnow(),
        )

        async with self.uow:
            await self.uow.generated_scripts.save(generated)

        return generated
