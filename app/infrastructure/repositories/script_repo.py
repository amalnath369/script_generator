from typing import List, Optional, Tuple

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.script import Script
from app.domain.repositories.script_repository import ScriptRepository
from app.infrastructure.database.models.scripts import ScriptModel


class IScriptRepository(ScriptRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def save(self, script: Script) -> None:
        model = ScriptModel(
            id=script.id,
            name=script.name,
            content=script.content,
            tags=script.tags,
            status=script.status,
        )
        self.session.add(model)
        await self.session.commit()


    async def get_by_id(self, script_id: str) -> Optional[Script]:
        model = await self.session.get(ScriptModel, script_id)
        if not model:
            return None

        return self._to_domain(model)

    
    async def update(self, script: Script) -> None:
        stmt = (
            update(ScriptModel)
            .where(ScriptModel.id == script.id)   
            .values(
                name=script.name,
                content=script.content,
                tags=script.tags,
                status=script.status,
                updated_at=func.now()
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()



    async def delete(self, script_id: str) -> None:
        stmt = delete(ScriptModel).where(ScriptModel.id == script_id)
        await self.session.execute(stmt)
        await self.session.commit()



    async def list_all(self, *, limit: int, offset: int) -> Tuple[int, List[Script]]:
        total_stmt = select(func.count()).select_from(ScriptModel)
        total = await self.session.scalar(total_stmt)

        stmt = (
            select(ScriptModel)
            .limit(limit)
            .offset(offset)
            .order_by(ScriptModel.created_at.desc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return total, [self._to_domain(model) for model in models]


    #  Mapper (infra → domain)
    def _to_domain(self, model: ScriptModel) -> Script:
        return Script(
            id=model.id,
            name=model.name,
            content=model.content,
            tags=model.tags,
            status=model.status,
        )
