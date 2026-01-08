from typing import List, Optional, Tuple

from sqlalchemy import select, update, delete, func
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
            model_name=script.model_name,
        )
        self.session.add(model)



    async def get_by_id(self, script_id: str) -> Optional[GeneratedScript]:
        model = await self.session.get(GeneratedScriptModel, script_id)
        if not model:
            return None

        return self._to_domain(model)
    
    
    async def get_by_script_id(self, script_id: str) -> Optional[List[GeneratedScript]]:
        stmt = select(GeneratedScriptModel).where(GeneratedScriptModel.script_id == script_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        if not models:
            return None

        return [self._to_domain(model) for model in models]
    

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



    async def list_all(self, *, limit: int, offset: int) -> Tuple[int, List[GeneratedScript]]:
        total_stmt = select(func.count()).select_from(GeneratedScriptModel)
        total = await self.session.scalar(total_stmt)

        stmt = select(GeneratedScriptModel).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return total, [self._to_domain(model) for model in models]


    # 🔁 Mapper
    def _to_domain(self, model: GeneratedScriptModel) -> GeneratedScript:
        return GeneratedScript(
            id=model.id,
            script_id=model.script_id,
            name=model.name,
            content=model.content,
            tags=model.tags,
            status=model.status,
            model_name=model.model_name,
            created_at=model.created_at if hasattr(model, 'created_at') else None,
            updated_at=model.updated_at if hasattr(model, 'updated_at') else None
        )
