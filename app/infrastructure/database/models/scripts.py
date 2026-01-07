from sqlalchemy import column, Integer,  Enum, String, Text, ARRAY
from app.infrastructure.database.models.base import BaseModel
from app.domain.entities.enums import ScriptStatus


class ScriptModel(BaseModel):
    __tablename__ = "scripts"

    id = column(Integer, primary_key=True, index=True)
    name = column(String, nullable=False, index=True)
    content = column(Text, nullable=False)
    tags = column(ARRAY(String), nullable=False)
    status = column(Enum(ScriptStatus), nullable=False, default=ScriptStatus.PENDING)