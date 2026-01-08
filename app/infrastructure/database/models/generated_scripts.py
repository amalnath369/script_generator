from sqlalchemy import Column, Integer, String, Text, ARRAY, Enum
from sqlalchemy import ForeignKey
from app.infrastructure.database.models.base import BaseDBModel
from app.infrastructure.database.models.scripts import ScriptModel
from app.domain.entities.enums import ScriptStatus



class GeneratedScriptModel(BaseDBModel):
    __tablename__ = "generated_scripts"

    script_id = Column(String, ForeignKey(ScriptModel.id), nullable=False)
    name = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), nullable=False, index=True)
    status = Column(Enum(ScriptStatus), nullable=False, default=ScriptStatus.PENDING)
    model_name = Column(String, nullable=False, index=True)