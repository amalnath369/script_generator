from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.generated_script import GeneratedScript
from app.domain.repositories.genrated_script_repository import GeneratedScriptRepository
from app.infrastructure.database.models.generated_scripts import GeneratedScriptModel


class IGeneratedScriptRepository(GeneratedScriptRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, script: GeneratedScript) -> None:
        model = GeneratedScriptModel(
            id=script.id,
            script_id=script.script_id,
            name=script.name,
            content=script.content,
            tags=script.tags,
            status=script.status,
        )
        self.session.add(model)

    async def get_by_id(self, script_id: str) -> Optional[GeneratedScript]:
        model = await self.session.get(GeneratedScriptModel, script_id)
        if not model:
            return None

        return self._to_domain(model)

    async def update(self, script_id: str, new_status: str) -> None:
        stmt = (
            update(GeneratedScriptModel)
            .where(GeneratedScriptModel.id == script_id)
            .values(status=new_status)
        )
        await self.session.execute(stmt)

    async def delete(self, script_id: str) -> None:
        stmt = delete(GeneratedScriptModel).where(
            GeneratedScriptModel.id == script_id
        )
        await self.session.execute(stmt)

    async def list_all(self) -> List[GeneratedScript]:
        stmt = select(GeneratedScriptModel)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    # 🔁 Mapper
    def _to_domain(self, model: GeneratedScriptModel) -> GeneratedScript:
        return GeneratedScript(
            id=model.id,
            script_id=model.script_id,
            name=model.name,
            content=model.content,
            tags=model.tags,
            status=model.status,
        )
