from typing import List, Optional

from sqlalchemy import select, update, delete
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

    async def get_by_id(self, script_id: str) -> Optional[Script]:
        model = await self.session.get(ScriptModel, script_id)
        if not model:
            return None

        return self._to_domain(model)

    async def update(self, script_id: str, new_status: str) -> None:
        stmt = (
            update(ScriptModel)
            .where(ScriptModel.id == script_id)
            .values(status=new_status)
        )
        await self.session.execute(stmt)

    async def delete(self, script_id: str) -> None:
        stmt = delete(ScriptModel).where(ScriptModel.id == script_id)
        await self.session.execute(stmt)

    async def list_all(self) -> List[Script]:
        stmt = select(ScriptModel)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]


    #  Mapper (infra → domain)
    def _to_domain(self, model: ScriptModel) -> Script:
        return Script(
            id=model.id,
            name=model.name,
            content=model.content,
            tags=model.tags,
            status=model.status,
        )
