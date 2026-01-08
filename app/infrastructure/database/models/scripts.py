from sqlalchemy import Column, Integer,  Enum, String, Text, ARRAY
from app.infrastructure.database.models.base import BaseDBModel
from app.domain.entities.enums import ScriptStatus


class ScriptModel(BaseDBModel):
    __tablename__ = "scripts"

    name = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), nullable=False)
    status = Column(Enum(ScriptStatus), nullable=False, default=ScriptStatus.PENDING)