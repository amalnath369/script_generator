from sqlalchemy import column, Integer, String, Text, ARRAY, Enum
from sqlalchemy import ForeignKey
from app.infrastructure.database.models.base import BaseModel
from app.infrastructure.database.models.scripts import ScriptModel
from app.domain.entities.enums import ScriptStatus



class GeneratedScriptModel(BaseModel):
    __tablename__ = "generated_scripts"

    id = column(Integer, primary_key=True, index=True)
    script_id = column(Integer, ForeignKey(ScriptModel.id), nullable=False)
    name = column(String, nullable=False, index=True)
    content = column(Text, nullable=False)
    tags = column(ARRAY(String), nullable=False)
    status = column(Enum(ScriptStatus), nullable=False, default=ScriptStatus.PENDING)
    