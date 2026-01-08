from dataclasses import dataclass   
from typing import List
from app.domain.entities.enums import ScriptStatus 
from datetime import datetime


@dataclass(kw_only= True)
class GeneratedScript:

    id: str
    script_id: str
    name: str
    content: str
    tags:  List[str]
    status: ScriptStatus = ScriptStatus.PENDING 
    model_name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

