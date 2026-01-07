from dataclasses import dataclass
from typing import List
from app.domain.entities.enums import ScriptStatus



@dataclass(frozen=True, kw_only= True)
class Script:

    id: str
    name: str
    content: str
    tags: List[str]
    status: str = ScriptStatus.PENDING

    def __post_init__(self):
        if not self.id:
            raise ValueError("Script id cannot be empty.")
        if not self.name:
            raise ValueError("Script name cannot be empty.")
        if not self.content:
            raise ValueError("Script content cannot be empty.")
        

        if self.content:
            lines = self.content.splitlines()
            if len(lines) > 1000:
                raise ValueError("Script content cannot exceed 1000 lines.")
    

    def update_status(self, new_status: ScriptStatus) -> "Script":
        return Script(
            id=self.id,
            name=self.name,
            content=self.content,
            tags=self.tags,
            status=new_status
        )
    